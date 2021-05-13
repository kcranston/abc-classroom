"""
abc-classroom.feedback
======================
"""

from pathlib import Path
import csv

from . import config as cf
from . import github
from . import utils

# or import just the function we need?
from . import scrub_feedback as sf


def scrub_html_files(source_dir):
    """Iterates through the source_dir, and for any html files found,
    scrubs them (which removes hidden test info). We also print
    """
    all_contents = Path(source_dir).rglob("*")
    all_files = [f for f in all_contents if f.is_file()]
    html_files = [f for f in all_files if f.suffix == "html"]
    for file in html_files:
        sf.scrub_feedback(file)
    print(
        "Found {} files in {}; scrubbed {} html files.".format(
            len(all_files), source_dir, len(html_files)
        )
    )


def feedback_files_exist(feedback_dir):
    """Checks if there are any non-hidden files in feedback_dir.
    Prints a warning if there are not. Helpful because utils.copy_files
    does not provide output on what's being copied (due to the use of
    python's copytree to do the heavy lifting)."""
    contents = Path(feedback_dir).rglob("*")
    all_files = [f for f in contents if f.is_file()]
    non_hidden = [f for f in all_files if not str(f).startswith(".")]
    if len(non_hidden) == 0:
        return False
    else:
        return True


def copy_feedback_files(assignment_name, push_to_github=False, scrub=False):
    """Copies feedback reports to local student repositories, commits the
    changes,
    and (optionally) pushes to github. Assumes files are in the directory
    course_materials/feedback/student/assignment. Copies all files in the
    source directory.

    Parameters
    -----------
    assignment_name: string
        Name of the assignment for which feedback is being processed.
    push_to_github: boolean (default = False)
        ``True`` if you want to automagically push feedback to GitHub after
        committing changes
    scrub: boolean
        If true, and we are moving an html file this will clean the html file
        before copying it over.

    Returns
    -------
        Moves feedback html files from the student feedback directory to the
        cloned_repos directory. Will commit to git and if ``push_to_github``
        is ``True``, it will also run ``git push``.
    """

    print("Loading configuration from config.yml")
    config = cf.get_config()

    # Get various paths from config
    # I think we do this a bunch so is it worth a helper for it?
    roster_filename = cf.get_config_option(config, "roster", True)
    course_dir = cf.get_config_option(config, "course_directory", True)
    clone_dir = cf.get_config_option(config, "clone_dir", True)
    materials_dir = cf.get_config_option(config, "course_materials", True)

    # get config option for files to ignore
    files_to_ignore = cf.get_config_option(config, "files_to_ignore", False)

    try:
        feedback_dir = Path(course_dir, materials_dir, "feedback")
        with open(roster_filename, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                student = row["github_username"]
                source_dir = Path(feedback_dir, student, assignment_name)
                # source_files = list(feedback_path.glob("*.html"))
                repo_name = "{}-{}".format(assignment_name, student)
                # The repos now live in clone_dir/assignment-name/repo-name
                destination_dir = Path(clone_dir, assignment_name, repo_name)
                if not destination_dir.is_dir():
                    print(
                        "Local student repository {} does not exist; skipping "
                        "student".format(destination_dir)
                    )
                    continue

                # are there any files in the feedback dir?
                if feedback_files_exist(source_dir):
                    if scrub:
                        scrub_html_files(source_dir)
                    utils.copy_files(
                        source_dir, destination_dir, files_to_ignore
                    )
                else:
                    print("Warning: No files found in {}".format(feedback_dir))
                # TODO: Turn this into a helper function lines 46 - 64 here
                # Don't copy any system related files -- not this is exactly
                # the same code used in the template.py copy files function.
                # this could become a helper that just moves files. I think
                # we'd call it a few times so it's worth doing... and when /
                # if we add support to move directories we could just add it
                # in one place.
                # files_to_ignore = cf.get_config_option(
                #     config, "files_to_ignore", True
                # )
                # This won't work when the entire path is provided
                # TODO: either parse files first and then create the site
                #  and paths or figure out another approach with generator
                # objects? maybe a list comprehension?
                # files_to_move = set(source_files).difference(files_to_ignore)
                #
                # for f in files_to_move:
                #     if scrub:
                #         # If f has an html extension and scrub is true
                #         # Clean the file and overwrite existing html
                #         sf.scrub_feedback(f)
                #         print("Removing hidden tests before copying")
                #     print(
                #         "Copying {} to {}".format(
                #             f.relative_to(course_dir), destination_dir
                #         )
                #     )
                #     shutil.copy(f, destination_dir)

                github.commit_all_changes(
                    destination_dir,
                    msg="Adding feedback for assignment {}".format(
                        assignment_name
                    ),
                )
                if push_to_github:
                    try:
                        github.push_to_github(destination_dir)
                    except RuntimeError as e:
                        print(e)
                        print(
                            "Push to GitHub failed for repo {}".format(
                                destination_dir
                            )
                        )

    except FileNotFoundError as err:
        # this could be the top-level feedback dir, the feedback dir for a
        # particular student, or the roster file
        print("Error! Could not find file or directory:")
        print(" ", err)


def copy_feedback(args):
    """
    Copies feedback reports to local student repositories, commits the changes,
    and (optionally) pushes to github. Assumes files are in the directory
    course_materials/feedback/student/assignment. Copies all files in the
    source directory, except those that match files_to_ignore in config.
    This is the command line implementation.

    Parameters
    ----------
    args : string
        Command line argument for the copy_feedback function. Options include:
        assignment: Assignment name
    github : boolean (default = False)
        If true, or --github used, push to GitHub. Otherwise only commit
        the change
    scrub : boolean (default = False)
        If true (exists), remove hidden tests from the html output
        before moving it to the student directory

    Returns
    -------
        Moves files from the student feedback directory to the
        cloned_repos directory. Will commit to git and if ``push_to_github``
        is ``True``, it will also run ``git push``.
    """
    assignment_name = args.assignment
    push_to_github = args.github
    scrub = args.scrub

    copy_feedback_files(assignment_name, push_to_github, scrub)
