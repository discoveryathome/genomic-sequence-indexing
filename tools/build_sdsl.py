"""Optional pinned SDSL comparator. Downloads/builds stay in ignored build/."""
from pathlib import Path
import os,subprocess
ROOT=Path(__file__).resolve().parents[1]
PIN='0546faf0552142f06ff4b201b671a5769dd007ad'
src=ROOT/'build/sdsl-lite';build=ROOT/'build/sdsl-build'
if not src.exists():
    subprocess.run(['git','clone','--depth','1','--branch','v2.1.1','https://github.com/simongog/sdsl-lite.git',str(src)],check=True)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip()==PIN
# Build-system-only compatibility fixes; algorithm sources are not tuned.
original=subprocess.check_output(['git','show','HEAD:CMakeLists.txt'],cwd=src,text=True)
patched=original.replace('-ffast-math','-fno-fast-math').replace(
    'OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")',
    'OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang" OR CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")')
(src/'CMakeLists.txt').write_text(patched)
# Modern Clang diagnoses these misspelled members in an unused LOUDS template.
header='include/sdsl/louds_tree.hpp'
original_header=subprocess.check_output(['git','show','HEAD:'+header],cwd=src,text=True)
(src/header).write_text(original_header.replace('tree.m_select1','tree.m_bv_select1').replace('tree.m_select0','tree.m_bv_select0'))
cmake=os.environ.get('CMAKE_BIN',str(ROOT/'.venv/bin/cmake'))
subprocess.run([cmake,'-S',str(src),'-B',str(build),'-DCMAKE_POLICY_VERSION_MINIMUM=3.5',
                '-DCMAKE_POSITION_INDEPENDENT_CODE=ON'],env={**os.environ,'BUILD_PORTABLE':'1'},check=True)
subprocess.run([cmake,'--build',str(build),'--target','sdsl','divsufsort','divsufsort64','-j2'],check=True)
subprocess.run([os.environ.get('CXX','c++'),'-O3','-std=c++11','-fno-fast-math','-fPIC','-shared',
 str(ROOT/'research/distribution-prep-20261022/sdsl_adapter.cpp'),
 '-I'+str(build/'include'),'-I'+str(src/'include'),'-I'+str(build/'external/libdivsufsort/include'),
 '-L'+str(build/'lib'),'-L'+str(build/'external/libdivsufsort/lib'),
 '-lsdsl','-ldivsufsort','-ldivsufsort64','-o',str(ROOT/'build/sdsl.dylib')],check=True)
