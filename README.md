# facial-recognition

Facial recognition for Carls.

### Harvesting Faces

This repository contains scripts for obtaining all Stalkernet profile images.
They require Python 3 and [requests](https://pypi.python.org/pypi/requests).

`python3 scrape_ldaps.py NTHREADS` scrapes Stalkernet for LDAP's with `NTHREADS` concurrent connections.
Using more than about 10 will put noticeable strain on Stalkernet, so be careful.
Every LDAP the program sees will be written to stdout, possibly with repeats.
So, `python3 scrape_ldaps.py NTHREADS | sort | uniq > ldaps.txt` will do what you want.

`python3 harvest_faces.py NTHREADS DEST` fetches images corresponding to the LDAP's provided through stdin, and writes them to the directory specified by `DEST` with `NTHREADS` concurrent connections.
The server serving these images is much beefier than the one serving Stalkernet.
I've had no problems with over 100 threads, but still be careful.
Images that are already in `DEST` will not be re-fetched.

If these scripts stop working or you see any log output with `WARNING` or `ERROR`, that probably means changes have been made to Stalkernet.
Raise an issue in this repository, and we'll update the scripts.

tl;dr `python3 scrape_ldaps.py 10 | sort | uniq | python3 harvest_faces.py 100 faces`

*Note: `.jpe` is equivalent to `.jpg`. The fact that this program uses the former is due to an implementation detail of a standard library module, which is in turn due to lexicographical ordering.*

### Training Azure with Faces

This repository also contains scripts for training Azure with the harvested faces.
They require Python 2 [cognitive_face](https://pypi.python.org/pypi/cognitive_face).


*TODO: document*
