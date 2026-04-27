#!/usr/bin/env bash
set -euo pipefail

echo "=== EBS Resize Helper ==="
echo "WARNING: This script changes your root filesystem layout."
echo "Recommendation: take an EBS snapshot or AMI backup before proceeding."
echo

if [[ $EUID -ne 0 ]]; then
  echo "Please run as root: sudo $0"
  exit 1
fi

echo "[1/7] Current block devices:"
lsblk
echo

echo "[2/7] Current filesystem usage:"
df -hT
echo

ROOT_SRC="$(findmnt -n -o SOURCE /)"
ROOT_FSTYPE="$(findmnt -n -o FSTYPE /)"
ROOT_MOUNT="/"

echo "Root source: $ROOT_SRC"
echo "Root filesystem type: $ROOT_FSTYPE"
echo

if ! command -v growpart >/dev/null 2>&1; then
  echo "[3/7] Installing growpart..."
  apt-get update
  apt-get install -y cloud-guest-utils
fi

if [[ "$ROOT_FSTYPE" == "xfs" ]]; then
  if ! command -v xfs_growfs >/dev/null 2>&1; then
    echo "[4/7] Installing xfsprogs..."
    apt-get install -y xfsprogs
  fi
fi

DISK="$(lsblk -no PKNAME "$ROOT_SRC" | head -n1)"
if [[ -z "${DISK:-}" ]]; then
  echo "Could not detect disk name from $ROOT_SRC"
  exit 1
fi

if [[ "$ROOT_SRC" =~ [0-9]$ ]]; then
  PART_NUM="$(echo "$ROOT_SRC" | sed -E 's/.*[^0-9]([0-9]+)$/\1/')"
  if [[ -z "${PART_NUM:-}" ]]; then
    echo "Could not detect partition number from $ROOT_SRC"
    exit 1
  fi

  echo "[5/7] Expanding partition /dev/$DISK partition $PART_NUM ..."
  growpart "/dev/$DISK" "$PART_NUM"
  TARGET="/dev/${DISK}p${PART_NUM}"
  [[ -b "$TARGET" ]] || TARGET="/dev/${DISK}${PART_NUM}"
else
  echo "No partition detected for root source; filesystem appears to be on the whole disk."
  TARGET="$ROOT_SRC"
fi

echo
echo "[6/7] Resizing filesystem..."
case "$ROOT_FSTYPE" in
  ext4|ext3|ext2)
    resize2fs "$TARGET"
    ;;
  xfs)
    xfs_growfs "$ROOT_MOUNT"
    ;;
  *)
    echo "Unsupported filesystem type: $ROOT_FSTYPE"
    exit 1
    ;;
esac

echo
echo "[7/7] Verification:"
lsblk
echo
df -hT

echo
echo "Done. The root filesystem should now reflect the new EBS size."
