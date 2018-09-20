# Change Log

## [Unreleased]
### Added

- `File` attribute
- `Email` attribute
- `Url` attribute

### Fixed
### Changed

- schema moved to directory so it's easier to group and add new attributes going forward, imports remain unaffected.

### Deprecated
### Removed
### Security


## [0.4.0]
### Added

- `ProxySchema`
- `apply_defaults` to apply schema defaults to a config dict

### Fixed

- `Schema.walk` now triggers the callback before entering subschemas

### Changed

- Schema now extends Attribute and is now working on instances rather than classmethod based
- Attribute name is now optional when attribute is member of list
- renamed `ListAttribute` to `List`
- renamed `StringAttribute` to `Str`
- renamed `IntAttribute` to `Int`
- renamed `FloatAttribute` to `Float`
- renamed `BooleanAttribute` to `Bool`
- renamed `DirectoryAttribute` to `Directory`

## [0.3.0]
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


