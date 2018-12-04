# Experimenting with grading workflows

This repository is the wild wild west playground for experimenting with workflows
that allow a course instructor to prepare material, distribute it to learners,
and for them to then turn in their homework.

## Try it out!

Install with `pip install -e.` from the directory of this README.

Then run `nbauthor master/01-lecture.ipynb`. This will take the master notebook,
and create a student and autograder version. The student version will be in
the `student/` subdirectory and the autograder version in `autograder/`.

The student directory can be distributed to students. It includes the questions
and code to run the grading steps that students can execute themselves.

To create a template repository for students use the `nbdistribute` command.
After running `nbauthor` on all the notebooks you want to include run:
`nbdistribute /tmp/student-template` to take the contents of the
`student/` directory and create a template repository from it at `/tmp/student-template`. Push this repository to GitHub and use it as the
template for your GitHub classroom assignment.

In the autograder directory you will find both the public and private tests,
but no notebook. The idea is that at a later stage students submit their
notebook and it is executed in the autograder directory by some server/robot.


## Assumptions

* instructor authors all work in a notebook
* instructor version of materials is published on a private GitHub repository
* student version of materials is published on a public GitHub repository
* answer to an assignment is multiple choice question
* answer to an assignment is code to be executed
* answer to an assignment is free form text
* partial answers to assignments receive partial credit
* assignments contain public parts
* assignments contain private parts
* public assignments can be executed by students on their notebook server
* solutions to public assignments can be seen by students
* solutions to private assignments can not be seen by students
* private assignments are executed by the "autograder" after students submit
  their work


## Questions

### How to check for "good style"?

* Check for general programming style of the notebook. Variable names that are
  sensible. All packages are imported at the top.
* Run `flake8` or `pep8` on notebook converted to a `.py` file?
* All imports should be at the top
* Imports at the top should also follow pep8. We know what they will be importing. can we create a functio ion that tests to ensure those things are in the right order?


### Can we spellcheck notebooks?
* Is there a spellcheck extension for notebooks?
  - (see this extension)[https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/spellchecker/README.html]. This only highlights words however. It's not great.


### How to check for "extra" stuff in the notebook?
* Can we check to ensure that only the packages used in the notebook are imported at the top?
Perhaps using (modulefinder)[https://docs.python.org/2/library/modulefinder.html] or something like it?
* Can we check for extra code, plots and outputs in the notebook that we didn't ask for?
  - I know that nbclean can somehow remove outputs from a notebook when converting. Could that be used to somehow identify outputs in cells where they should be no outputs?
