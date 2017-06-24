ifeq ($(wildcard Makefile.inc), )
	$(error Configuration not found. Run ./configure first)
endif

include Makefile.inc

# define all programs
PROGRAMS = nrfd
include Makefile.examples
