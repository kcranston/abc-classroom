# Tests for clone script
from pathlib import Path

import abcclassroom.feedback as abcfeedback


def test_scrub_html_files(course_with_feedback):
    """Test scrub_html_files function (iteration through feedback dir to
    identify and scrub html files). Does not test the changes to the html
    files from the scrub utility function - that's out of scope here.
    """
    config, assignment_name, students = course_with_feedback
    student = students[0]
    course_dir = config["course_directory"]
    materials_dir = config["course_materials"]
    feedback_dir = Path(course_dir, materials_dir, "feedback")
    source_dir = Path(feedback_dir, student, assignment_name)
    (allfiles, htmlfiles) = abcfeedback.scrub_html_files(source_dir)
    assert allfiles == 2
    assert htmlfiles == 1


def test_feedback_files_exist(tmp_path):
    """Test that the feedback_files_exist correctly returns True when
    there are non-hidden files and False when there are no non-hidden
    files.
    """
    test_dir = Path(tmp_path, "test_dir")
    # make a dir with only a hidden file
    test_dir.mkdir()
    Path(test_dir, ".hiddenfile.txt").touch()
    assert not abcfeedback.feedback_files_exist(test_dir)
    # add a non-hidden file
    Path(test_dir, "feedback.html").touch()
    assert abcfeedback.feedback_files_exist(test_dir)


def test_copy_feedback_files(course_with_feedback):
    config, assignment_name, students = course_with_feedback
    student = students[0]
    repo_name = "{}-{}".format(assignment_name, student)
    course_dir = config["course_directory"]
    clone_dir = config["clone_dir"]
    destination_dir = Path(course_dir, clone_dir, assignment_name, repo_name)
    starting_files = list(destination_dir.iterdir())
    abcfeedback.copy_push_feedback(
        assignment_name, push_to_github=False, scrub=False
    )
    ending_files = list(destination_dir.iterdir())
    assert len(ending_files) > len(starting_files)
    assert Path(destination_dir, "feedback.html").exists()
    assert Path(destination_dir, "not_html.txt").exists()


# this could be the top-level feedback dir, the feedback dir for a
# particular student, or the roster file

# def test_copy_feedback_no_feedback_dir(tmp_path):
