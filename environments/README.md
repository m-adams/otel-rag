# Environments

This folder is intended for maintaining multiple configurations. You can place your configuration files here and create symbolic links to them as needed. These files will be ignored by Git.

## Usage

1. Place your configuration files in this directory.
2. Create symbolic links to these files in the appropriate locations.

## Example

```sh
ln -s /path/to/this/folder/config-file /path/to/symlink
```

## Note

Ensure that your `.gitignore` is set up to ignore the files in this directory.