# Shifted-dataset adapters

Unseen clients retain their base-client sample count. A deterministic fraction
(`federated.unseen_data_fraction`) of their samples is replaced from an
external pool. Replacement is label-aligned whenever the external pool
contains the requested base label; the run records a fallback count if a label
is missing.

## CIFAR-10 + CIFAR-10-C

Use `unseen_shift.type: cifar10_c`. The adapter memory-maps the official
corruption arrays and supports one or more corruption names and severities
1--5.

## FEMNIST + Chars74K

Point `data_root` at the directory whose direct child folders are the Chars74K
classes (for the standard layout, the `Sample001` ... `Sample062` directory).
The default `chars74k_sample_order` strategy maps `Sample001` to label 0,
through `Sample062` to label 61.

```yaml
federated:
  unseen_data_fraction: 0.4
  unseen_shift:
    enabled: true
    type: chars74k
    data_root: data/chars74k/English/Img/GoodImg/Bmp
```

## GTSRB + CTSDB/GTSDB

Point `data_root` at an ImageFolder tree and provide an explicit mapping from
external folder names to GTSRB labels. This prevents silently treating
unrelated class indices as equivalent.

```yaml
unseen_shift:
  enabled: true
  type: ctsdb
  data_root: data/ctsdb/classification
  label_map_file: configs/label_maps/ctsdb_to_gtsrb.yaml
```

The mapping file is a YAML/JSON object such as:

```yaml
speed_limit_60: 3
stop: 14
```

## Stanford Cars + CompCars

CompCars and Stanford Cars do not expose an identical ordered label space.
Use an ImageFolder tree plus a curated make/model mapping rather than relying
on directory order:

```yaml
unseen_shift:
  enabled: true
  type: compcars
  data_root: data/compcars/imagefolder
  label_map_file: configs/label_maps/compcars_to_stanford_cars.yaml
```

Only mapped classes are loaded. A configuration that maps no files into the
base task fails before training instead of falling back to synthetic data.

