# README

This model is used to test cases with

- circular dependencies (circular model)
- model which sharing 
  - top_level uses sub_project_1 and sub_project_2, each subproject uses common
  - other project is unrelated to top_level, but uses common as well
- top_level defines utils module, defining C as int32 const, and other defines also utils module, defining C as float32. 
  Both projects are unrelated, 