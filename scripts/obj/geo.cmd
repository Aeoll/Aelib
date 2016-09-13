# Default script run when a geometry object is created
# $arg1 is the name of the object to create

\set noalias = 1
if ( "$arg1" != "" ) then
    opparm $arg1 use_dcolor( 0 )
    opproperty -f -F Render $arg1 mantra default_geometry
#   Lock the scales if you want to play it more safely:
#   chlock $arg1 +s?
endif
