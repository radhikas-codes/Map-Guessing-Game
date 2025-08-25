import turtle

screen = turtle.Screen()
screen.title("south america Countries")
image = "south_america_map.gif"
screen.addshape(image)
turtle.shape(image)

def get_mouse_click_coor(x,y):
    print(x,y)

turtle.onscreenclick(get_mouse_click_coor)
turtle.mainloop()
