# This script serves the purpose of a general layout
import PySimpleGUI as sg
import os, io

from inference_gfpgan_gui import inferenceGFPGAN
from multiprocessing import Process
from PIL import Image, ImageTk

"""
Simple Image Browser based on PySimpleGUI
--------------------------------------------
There are some improvements compared to the PNG browser of the repository:
1. Paging is cyclic, i.e. automatically wraps around if file index is outside
2. Supports all file types that are valid PIL images
3. Limits the maximum form size to the physical screen
4. When selecting an image from the listbox, subsequent paging uses its index
5. Paging performance improved significantly because of using PIL

Dependecies
------------
Python3
PIL
"""


# ------------------------------------------------------------------------------
# use PIL to read data of one image
# ------------------------------------------------------------------------------


def get_img_data(f, maxsize=(1200, 850), first=False):
    """Generate image data using PIL
    """
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)
# ------------------------------------------------------------------------------


def runInference(inputs, outputFolder):
    # run inference
    inferenceGFPGAN(inputs, outputFolder)
    complete = True
    return complete


def inferenceWindow(text):
    layoutRunning = [[sg.Text(f"Running restoration on {text}...")]]

    # Create the window
    windowRunning = sg.Window("Demo", layoutRunning)

    # Create an event loop
    while True:
        event, values = windowRunning.read()
        # End program if user closes window or
        # presses the OK button
        if event == "OK" or event == sg.WIN_CLOSED:
            break

    windowRunning.close()


def main():
    # Get the folder containin:g the images from the user
    inputFolder = sg.popup_get_folder('Folder with images to restore', default_path='')

    if not inputFolder:
        sg.popup_auto_close('You need to select a folder.')
        raise SystemExit()

    # PIL supported image types
    img_types = (".png", ".jpg", "jpeg", ".tiff", ".bmp")

    # get list of files in folder
    flist0 = os.listdir(inputFolder)

    # create sub list of image files (no sub folders, no wrong file types)
    fnames = [f for f in flist0 if os.path.isfile(
        os.path.join(inputFolder, f)) and f.lower().endswith(img_types)]

    num_files = len(fnames)                # number of images found
    if num_files == 0:
        sg.popup('No files in folder')
        raise SystemExit()

    del flist0                             # no longer needed

    # make these 2 elements outside the layout as we want to "update" them later
    # initialize to the first file in the list
    filename = os.path.join(inputFolder, fnames[0])  # name of first file in list
    image_elem = sg.Image(data=get_img_data(filename, first=True))
    filename_display_elem = sg.Text(filename, size=(80, 3))
    file_num_display_elem = sg.Text('File 1 of {}'.format(num_files), size=(15, 1))

    # define layout, show and read the form
    col_files = [[sg.Text('Select image to restore and click Next. \nTo restore all images in folder click: Restore all files',size=(80,3))], [sg.Listbox(values=fnames, change_submits=True, size=(60, 30), key='listbox')],
                [sg.Button('Next', size=(8, 2)), sg.Button('Restore all images in folder', size=(24, 2)), file_num_display_elem]]

    layout = [[sg.Column(col_files)]]

    window = sg.Window('Select images to restore', layout, return_keyboard_events=True, use_default_focus=False)

    # loop reading the user input and displaying image, filename
    i = 0
    while True:
        # read the form
        event, values = window.read()
        print(event, values)
        # perform button and keyboard operations
        if event == sg.WIN_CLOSED:
            break
        elif event in ('Next', 'MouseWheel:Down', 'Down:40', 'Next:34'):
            # restore selected image:
            print(f"filepath: {filename}")
            input = filename
            text = 'image'
            inputType = 'single image'
            # close window to run GFPGAN
            window.close()

        elif event in ('Restore all images in folder', 'MouseWheel:Up', 'Up:38', 'Prior:33'):
            # path to foler
            input = inputFolder
            text = 'images'
            inputType = 'folder'

            # close window to run GFPGAN
            window.close()

        elif event == 'listbox':            # something from the listbox
            f = values["listbox"][0]            # selected filename
            filename = os.path.join(inputFolder, f)  # read this file
            print(filename)
        else:
            filename = os.path.join(inputFolder, fnames[i])

    # Request output folder
    outputFolder = sg.popup_get_folder('Output folder: where do you want to the restored images to be placed', default_path='')

    layoutRunning = [[sg.Text(f"Input type: {inputType}")],
        [sg.Text(f'Input location: {input}')],
        [sg.Text(f'Output folder: {outputFolder}')],
        [sg.Text("Click button if ready to run restoration")],
        [sg.Button("Run restoration"), sg.Button("Cancel")]]

    # Create the window
    windowRunning = sg.Window("Summary", layoutRunning)

    # Create an event loop
    while True:
        event, values = windowRunning.read()
        print(event)
        # End program if user closes window or
        # presses the OK button
        if event == sg.WIN_CLOSED:
            break
        elif event in ('Run restoration', 'MouseWheel:Down', 'Down:40', 'Next:34'):
            inferenceGFPGAN(input, outputFolder)
            break
        elif event in ('Cancel', 'MouseWheel:Down', 'Down:40', 'Next:34'):
            break

    windowRunning.close()

    layoutEnd = [[sg.Text(f"Restoration run successfully!")]]

    # Create the window
    endWindow = sg.Window("Restoration complete!", layoutEnd)
    # Create an event loop
    while True:
        event, values = endWindow.read()
        if event == sg.WIN_CLOSED:
            break


    endWindow.close()


if __name__=="__main__":
    main()
