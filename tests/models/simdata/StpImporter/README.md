# StpImporter Test

Unit test for **stpimporter**. Should be augmented with new features/defects.

## SCADE Suite Project

- Scade Model
    
  All _StpImporter_ files

- SCADE Test project for the model

  Content of _TestProject_ folder, with various *.sss* files and the _.stp_ file

Opening *StpImporter.vsw* provides the complete environment.

## Swan Project

- SI

  Contains the import of the Suite project. _renamings.log_ file is key to get proper names between Scade and Swan.

- TestSi

  Scade One test harness for _SI/StpImporter project_. 
  
  The project references _.sd_ files in *sd_refs* folder as resources.

  It uses the imported Scade One project as a library.



## Oracle

The files in the *sd_refs* folder are the reference for the current version of *stpimporter*.

