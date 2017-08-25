with import <nixpkgs> {};

let
  cognitive_face = with python27Packages; buildPythonPackage rec {
    pname = "cognitive_face";
    version = "1.3.1";
    name = "${pname}-${version}";

    propagatedBuildInputs = [ pep8 pillow pyflakes pylint requests2 ];

    src = pkgs.fetchurl {
      url = "mirror://pypi/${builtins.substring 0 1 pname}/${pname}/${name}.tar.gz";
      sha256 = "1hgjyayjyl8giiw2p0szy8af32alsb5mgywzah1aa067xk6lvh96";
    };

    # Tests require manual configuration
    doCheck = false;
  };

in
  stdenv.mkDerivation {
    name = "env";
    buildInputs = [
      python3
      python3Packages.requests2
      python27
      cognitive_face
    ];
  }
