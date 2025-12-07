#! /bin/bash
echo "Clean uploads"
cd uploads
rm -fr *
cd ..
echo "Clean html_render"
cd html_render
rm -fr *
cd ..
echo "Clean pdf"
cd pdf
rm -fr *
cd ..
echo "Clean svg"
cd svg
rm -fr *
cd ..
echo "Done."
