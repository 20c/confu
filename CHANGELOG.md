# Change Log

## [Unreleased]
### Added
### Fixed
### Changed
### Deprecated
### Removed
### Security

## [0.6.0]
### Added
- `blank` argument for `Str` attribute - specifies whether value can be blank or not, defaults to `False`

### Fixed
- proxy schema needs to be able to apply defaults (#10)
- issue where list validation would sometimes lead to duplicate items added to the list

### Changed
- `Directory` attribute will forfeit validation if `blank` is `True` and value is `""`

## [0.5.2]
### Fixed
- recursive directory creation for Directory Attribute if `create` is specified

## [0.5.1]
### Fixed
- `apply_defaults` now properly works with nested items

## [0.5.0]
### Added

- `File` attribute
- `Email` attribute
- `Url` attribute
- `IpAddress` attribute
- `Schema` attribute now has an optional `item` argument that if set allows for validation of dicts with arbitrary keys.
- Support for ConfigParser instances in validate

### Changed

- schema moved to directory so it's easier to group and add new attributes going forward, imports remain unaffected.
- `validate` will now pass **kwargs on to `Schema.validate`
- Facsimile to Ctl


## [0.4.0]
### Added

- `ProxySchema`
- `apply_defaults` to apply schema defaults to a config dict
- `Config` object

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


