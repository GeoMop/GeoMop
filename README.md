# GeoMop &middot; [![Travis (.org)](https://img.shields.io/travis/GeoMop/GeoMop.svg?style=flat-square)](https://travis-ci.org/GeoMop/GeoMop) [![Coveralls github](https://img.shields.io/coveralls/github/GeoMop/GeoMop.svg?style=flat-square)](https://coveralls.io/github/GeoMop/GeoMop)
Toolbox for preparation and running complex hydrogeological simulations in particular using [Flow123d](https://flow123d.github.io) simulator of 
transport and mechanical processes in fractured media.

# Installation
Installation packages for Windows and Debian Linux available at the 
project [homepage](https://geomop.github.io).

Installation under Windows uses a standard installer. 
The Debian installation uses standard DEB package.

The package consists of the four separated graphical applications:
    
**Layers** - preparation of layered computational geometry from the GIS data

**Model Editor** - editor of the main Flow123d input file in YAML format

**Jobs Panel** - running and management of job on distributed computational resources

**VISIP** - arrangement of complex computing scenarios 

[Jenkins CI server](https://ci3.nti.tul.cz)

| CI build | [![Build Status](http://ci3.nti.tul.cz/buildStatus/icon?job=gm-build)](http://ci3.nti.tul.cz/job/gm-build) |
| ----- | ---- |
| Tests | [![Test Status](http://ci3.nti.tul.cz/buildStatus/icon?job=gm-linux-tests)](http://ci3.nti.tul.cz/job/gm-linux-tests/) |

## Development rules and notes

### Sources
- In order to use relative imports of modules within package the prefered format of imports is:
    
    from <package> import <module> as <new_module_name>

### Tests
- use @pytest.mark.<the_mark> to set marks to the test functions, in particular
  to mark tests that needs specific environment, e.g. ssh setup. Standard set of marks:
  
  - ssh_metacentrum - use ssh connection to the metacentrum servers
  - metacentrum - run on metacentrum, e.g. test PBS 
  - slow - tests that take more then 5s
  - skip - python skip these tests
  - qt - tests using QApplication
  
- TODO: use [pytest-qt](http://pytest-qt.readthedocs.io/en/latest/intro.html) to test function of Qt widgets  
  
## Authors

doc. Mgr. Jan Březina, Ph.D. <sup>1</sup> \
Ing. Radek Srb <sup>1</sup> \
Ing. Martin Špetlík <sup>1</sup>

<sup>1</sup> Ústav nových technologií a aplikované informatiky, Fakulta mechatroniky, informatiky a mezioborových studií, Technická univerzita v Liberci
