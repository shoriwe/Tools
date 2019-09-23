import ui
from sys import argv
from os.path import join, isdir
from shutil import copy2, copytree
from os import listdir, getcwd
from appex import get_file_paths

# This function is better that the original from shutil
# Thanks to @atzz from StackOverflow
def betterCopyTree(src, dst, symlinks=False, ignore=None):
    for item in listdir(src):
        s = join(src, item)
        d = join(dst, item)
        if isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            copy2(s, d)
# Faster join and prevent join "step back directories" and "current working directories"
def betterJoin(base, target):
    if target == '..':
        path = '/'.join(base.split('/')[:-1])
    elif target == '.':
        path = base
    else:
        path = join(base, target)
    if path[-1] == '/':
        path = path[:-1]
    return path

# Function that is called to change the current directory
# it is callled by "Back" button and when the user selects a row of the tableview
def cd(sender):
    if sender.title == 'Back':
        # this ide is called when user press "Back" button
        current_dir = view.data_source.current_dir
        view.data_source.update_items(betterJoin(current_dir, '..'))
    else:
        # This side is called when the user selects a row
        row = view.selected_row[1]
        # This itee is a directory
        item = view.data_source.items[row]
        # Use the current dir to create a new complete path to the selected directory
        current_dir = view.data_source.current_dir
        view.data_source.update_items(betterJoin(current_dir, item))
    # Always reload the view (this updates the tableview values)
    view.reload()

# Quicker and cleanest way to create a button
def buttonCreator(title, action, frame, color):
    button = ui.Button()
    button.title = title
    button.action = action
    button.frame = frame
    button.bg_color = color
    button.border_width = 1
    button.corner_radius = 1
    button.border_color = '#010100'
    button.tint_color = '#000000'
    return button

# This delegate help the table view with it's  selected rows
class TableViewDelegate(object):
    # Function that is executed every time a row is selected
    def tableview_did_select(self, tableview, section, row):
        cd(tableview)

# Get the home directory
def get_home():
    pwd = getcwd()
    while len(pwd.split("/")) > 8:
        pwd = betterJoin(pwd, "..")
    return pwd
# Data source
# For some reason tableview requires a object to manage it's values.
# This only grabs values and make it acceible for the tableview
# It's customized for this script
class CustomDataSource(object):
    def __init__(self, pwd=get_home()):
        # Items for the tableview
        self.items = None
        # Paths that were passed when the script is called from SHARE
        self.__share_paths = get_file_paths()
        # Easier way to manage the working directory
        # Note that all is virtual so this script never chdir in a directory
        self.current_dir = None
        # Update the values with the content
        self.update_items(pwd)
        # This three values are used for the script frames
        screen_size = ui.get_screen_size()
        cell = ui.TableViewCell() # this really is only necessary for the calculation of the copy button frame but is
        # never used
        # This is used for the calculation of the cellframe
        cell_frame = cell.frame

        self.disabled_buttons = []
        # Reference frame for the cell
        self.button_cell_frame_ref = (
        (screen_size[0] * 320) / 414, (cell_frame[3] * 15) / 44, (cell_frame[2] * 100) / 414, (cell_frame[3] * 30) / 44)
    # Update the values of the items with the content of the current directory
    def update_items(self, pwd):
        self.items = list(filter(lambda file: isdir(betterJoin(pwd, file)), listdir(pwd)))
        # update  the new current directory
        self.current_dir = pwd
    #  Creation of the button for copy files
    def copyhereButton(self):
        button = buttonCreator('Copy here', self.copy, self.button_cell_frame_ref, '#80f228')
        return button
    # Copy function called by "Copy here" button
    def copy(self, sender):
        item = sender.superview.text_label.text
        # Handler to extract the path  variable from the for loop
        path = None
        # Check the origin of the files to copy
        if len(argv[1:]):
            args = argv[1:]
        else:
            args = self.__share_paths
        #  for each file the user want to copy
        for file in args:
            # Complete path to target folder
            path = betterJoin(self.current_dir, item)
            # When the source file is a folder
            if isdir(file):
                target_folder = file.split('/')[-1] # Copytree requires a not existing folder as target
                # Copy the fie
                betterCopyTree(file, betterJoin(path, target_folder))
            else:
                # When source is a file
                copy2(file, path)
        # Disable the button so the user can't overwrite unnecessarily the file
        sender.enabled = False
        # add the button
        self.disabled_buttons.append(path)
    # Function that creates eaach cell for the tableview
    def tableview_cell_for_row(self, tableview, section, row):
        # Cell object that is added as subview to the tableview
        cell = ui.TableViewCell()
        # Add the cell the element corresponding with the row gived
        cell.text_label.text = self.items[row]
        # Button that is added to the cell (this is the "Copy here" button)
        button = self.copyhereButton()
        # Check if the button was disabled before
        if betterJoin(self.current_dir, self.items[row]) in self.disabled_buttons:
            button.enabled = False
        # Finally add the button as a subview of the cell and return the cell
        cell.add_subview(button)
        return cell
    # Function necessary for the construction of the data source it returns the len of the items list
    def tableview_number_of_rows(self, tableview, section):
        return len(self.items)

# This is the subview
view = ui.TableView()


def main():
    # Add a title to differentiate in the "cd" function from the "Back" button and when a row is selected
    view.title = 'Copy'
    # Create the data source for the tableview
    data_source = CustomDataSource()
    # Add the data source to the tableview
    view.data_source = data_source
    # add  the "Back" button to the table view
    view.right_button_items = [ui.ButtonItem(title='Back', action=cd)]
    # Make a relation between the tableview and the custom delegate
    view.delegate = TableViewDelegate()
    # Finally start the ui
    view.present()


if '__main__' == __name__:
    main()