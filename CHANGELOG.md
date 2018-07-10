# Change Log

## [Unreleased]
### Added

- py2.7 support
- DirectoryAttribute
- generator.generate shortcut

### Fixed

- validation: schema validation returning None value
- validation: warnings raised with the wrong exception type
- exceptions: can now have integers in config path (from list index for example)

### Changed

- renamed `UnicodeAttribute` to `StringAttribute` that is now looking for either string or unicode types during validation

### Deprecated
### Removed
### Security
