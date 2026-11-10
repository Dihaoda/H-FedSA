#!/usr/bin/env bash
set -euo pipefail

destination="${1:-data/cifar10-c-download}"
archive="${destination}/CIFAR-10-C.tar"
expected_md5="56bf5dcef84df0e2308c6dcbcbbd8499"

mkdir -p "${destination}"

if [[ -f "${archive}" ]] && echo "${expected_md5}  ${archive}" | md5sum --check --status; then
  echo "CIFAR-10-C archive is already present and verified."
else
  sources=(
    "https://zenodo.org/records/2535967/files/CIFAR-10-C.tar?download=1"
    "https://hf-mirror.com/datasets/torch-uncertainty/CIFAR-C/resolve/main/CIFAR-10-C.tar?download=true"
  )
  downloaded=false
  for source in "${sources[@]}"; do
    echo "Downloading CIFAR-10-C from ${source}"
    if wget --continue --output-document "${archive}" "${source}"; then
      if echo "${expected_md5}  ${archive}" | md5sum --check --status; then
        downloaded=true
        break
      fi
      echo "Downloaded file failed the expected MD5 check." >&2
    fi
  done
  if [[ "${downloaded}" != true ]]; then
    echo "Unable to download and verify CIFAR-10-C." >&2
    exit 1
  fi
fi

if [[ -f "${destination}/CIFAR-10-C/gaussian_noise.npy" \
   && -f "${destination}/CIFAR-10-C/shot_noise.npy" \
   && -f "${destination}/CIFAR-10-C/labels.npy" ]]; then
  echo "CIFAR-10-C is already extracted."
else
  echo "Extracting ${archive}"
  tar -xf "${archive}" -C "${destination}"
fi

echo "CIFAR-10-C ready at ${destination}/CIFAR-10-C"

