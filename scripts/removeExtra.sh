#! /bin/sh

#assume executing this script from the current directory (scripts/). For now, not accepting params. TODO


find ../ -name '*.pyc'  -exec rm -rf {} \;

find ../ -name '*~'  -exec rm -rf {} \;

#rm -r ../db ;

#rm -r ../media/noteattachments ;

#rm ../osl.log ;


