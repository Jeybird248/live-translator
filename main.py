from PIL import ImageGrab, Image, ImageTk
import win32gui
from win32api import GetSystemMetrics
from tkinter import *
from tkinter import ttk
import pyautogui
import cv2
import pytesseract
import numpy as np
from translate import Translator

width = int(GetSystemMetrics(0) / 2)
height = int(GetSystemMetrics(1) - 100)
pytesseract.pytesseract.tesseract_cmd = ##
custom_config = r'-l kor --psm 6'
kernel = np.ones((2,2),np.uint8)

def getApplication():
    applications = []
    for x in pyautogui.getAllWindows():  
        applications.append(x.title)
    return applications

def findWindow():
    hwnd = win32gui.FindWindow(None, variable.get())
    win32gui.MoveWindow(hwnd, 0, 0, width, height, True)
    win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    img = ImageGrab.grab(bbox)
    w, h = img.size
    return img.crop((0, 32, w, h))

def translate():
    cv2.namedWindow('window', cv2.WINDOW_KEEPRATIO)
    hwnd = win32gui.FindWindow(None, "window")
    img = preview(None).copy()
    w2 = img.width * 2
    h2 = img.height * 2
    win32gui.MoveWindow(hwnd, width, 0, width, int(h2 * width / w2), True)
    win32gui.SetForegroundWindow(hwnd)
    while True:
        img = np.array(preview(None).resize((w2 * 2, h2 * 2))).copy()
        display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,11)
        
        _ , img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
        translator = Translator(to_lang="en", from_lang = "ko")
        boxes = pytesseract.image_to_data(img, output_type="dict", config=custom_config)
        boxes = overlap(boxes)
        for i in range(len(boxes)):
            (x, y, w, h) = (boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3])
            cv2.rectangle(display, (x, y), (w, h), (0, 0, 0), -1)
            cv2.rectangle(display, (x, y), (w, h), (0, 0, 255), 2)
            cv2.putText(display, translator.translate(boxes[i][4]), (x, h), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("window", display)
        # cv2.imshow("img", img)
        if cv2.waitKey(27) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
        break

def merge_boxes(box1, box2):
    return [min(box1[0], box2[0]), 
         min(box1[1], box2[1]), 
         max(box1[2], box2[2]),
         max(box1[3], box2[3]), 
         box1[4] + " " + box2[4]]

def overlap(dict):
    sorted = []
    text_list = dict["text"]
    x_list = dict["left"]
    y_list = dict['top']
    width_list = dict['width']
    height_list = dict['height']
    conf_list = dict["conf"]
    for i in range(0, len(x_list)):
        if (conf_list[i] > 80 and text_list[i]):
            curr_box = [x_list[i], y_list[i], x_list[i] + width_list[i], y_list[i] + height_list[i], text_list[i]]
            for j in range(i + 1, len(x_list)):
                if (conf_list[j] > 80 and text_list[j]):
                    compare_box = [x_list[j], y_list[j], x_list[j] + width_list[j], y_list[j] + height_list[j], text_list[j]]
                    print(curr_box, compare_box)
                    if (abs(curr_box[1] - compare_box[1]) <= curr_box[3] - curr_box[1]):
                        if (abs(curr_box[0] - compare_box[0]) <= curr_box[2] - curr_box[0] + 50):
                            curr_box = merge_boxes(curr_box, compare_box)
                            conf_list[j] = 0
            sorted.append(curr_box)
    return sorted

def preview(self):
    global cropimg
    img = findWindow()    
    widthSVal = int(widthS.get())
    widthEVal = int(widthE.get())
    heightSVal = int(heightS.get())
    heightEVal = int(heightE.get())
    height2=heightEVal - heightSVal
    width2=widthEVal - widthSVal
    root.geometry('{2}x{3}+{0}+{1}'.format(width + 50, 50, width2 + 600, height2 + 400))
    cropimg = ImageTk.PhotoImage(img.crop((widthSVal, heightSVal, widthEVal, heightEVal)))
    canvas.config(width=width2, height=height2)
    output = ImageTk.getimage(cropimg)
    canvas.create_image(0, 0, image=cropimg, anchor="nw")
    return output

def refresh():
    w["menu"].delete(0, "end")
    apps = getApplication()
    for app in apps:
        w["menu"].add_command(label=app, command=lambda name=app: variable.set(name))

if __name__ == "__main__":
    root = Tk()
    root.title("Pick a Window to Translate")
    root.geometry('600x400+{0}+{1}'.format(width + 50, 50))
    variable = StringVar(root)
    cropimg = PhotoImage()
    apps = getApplication()
    #############FRAMES##################
    previewframe = Frame(root)
    previewframe.pack(side="right", padx=10, pady=10)
    inputframe = Frame(root)
    inputframe.pack(side="left")
    ############CANVAS###################
    canvas = Canvas(previewframe, width=0, height=0)
    canvas.pack(padx=10, pady=10, expand = True)
    canvas.bind('<Double-1>', preview)
    #############BUTTONS & MENUS##################
    w = OptionMenu(root, variable, command = preview, *apps)
    w.pack()
    B = ttk.Button(root, text ="Press to Translate Window", command = translate)
    B.pack()
    C = ttk.Button(root, text ="Press to Update List", command = refresh)
    C.pack()
    #############LABELS##################
    previewlabel = Label(previewframe, text="Preview:").pack(padx=20, pady=10)
    label1 = Label(inputframe, text="Enter the starting width")
    label1.pack()
    widthS = Entry(inputframe, width=25)
    widthS.pack(padx=20, pady=10)
    widthS.insert(END, "30")
    label2 = Label(inputframe, text="Enter the ending width")
    label2.pack()
    widthE = Entry(inputframe, width=25)
    widthE.pack(padx=20, pady=10)
    widthE.insert(END, "900")
    label3 = Label(inputframe, text="Enter the starting height")
    label3.pack()
    heightS = Entry(inputframe, width=25)
    heightS.pack(padx=20, pady=10)
    heightS.insert(END, "250")
    label4 = Label(inputframe, text="Enter the ending height")
    label4.pack()
    heightE = Entry(inputframe, width=25)
    heightE.pack(padx=20, pady=10)
    heightE.insert(END, "700")
    ###############################
    root.mainloop()
