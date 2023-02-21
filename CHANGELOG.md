# Changelog

We are currently working on porting this changelog to the specifications in
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Version: 1.2.0] - 

### Fixed
* homogeneous=False mode now correctly prints messages

### Changed
* Reworked internals of how time and display checks are handled. This has the
  user-facing-effect that messages will not print unless `time_thresh` seconds
  have passed.

## [Version: 1.1.0] - Released 2023-01-13  

### Added
* New argument `homogeneous` which can be set to True to enable a speed
  optimization. Default to `auto`, which uses a heuristic to determine a good
  setting for this in most cases.

### Fixed
* `time_thresh` is now respected when calculating dynamic display updates
* Fixed an issue where sometimes the final message would not display.


## [Version: 1.0.1] - Released 2022-10-07 

### Fixed
* `ProgIter.format_message` returned to its original signature. The
  `ProgIter.format_message_parts` now contains the new signature.


## [Version: 1.0.0] - Released 2022-10-01

### Changed
* `ProgIter.format_message` return value has changed.

### Removed
* Support for Python <= 3.6

### Fixed
* Issue 21

## [Version: 0.1.4] - Released 2021-12-07

### Fixed
* `ProgIter` now correctly checks if it needs to displays a message on every iteration.
* fixed uninitialized `_cursor_at_newline ` variable in `ProgIter`.

### Changed
* `ProgIter.step` now respects update freq, and will not update the estimates
  if too few iterations have passed.

* Added ubelt updates


## [Version: 0.1.3] - Released

* Undocumented


## [Version: 0.1.2] - Released 2021-12-07

### Fixed 
* Setting `total=0` now correctly shows progress as `0/0`


## [Version: 0.1.0] - Released 

### Changed 
* Add CircleCI tests
* Reorganized runtime versus test dependencies
* Reduced import time
* Cleanup some docs
 

## [Version: 0.0.3] - Released

### Added
* Can now inform ProgIter of chunksize to get Hz in items per second instead of chunks per second.

[Version: 0.0.1] - Released

### Added
* Initial version ported from ubelt
## Version 0.1.5 - Unreleased


