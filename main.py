# Convex hull
#
# Usage: python main.py [-d] [-np] file_of_points
#
#   -d sets the 'discardPoints' flag
#   -np removes pauses
#
# You can press ESC in the window to exit.
#
# You'll need Python 3 and must install these packages:
#
#   PyOpenGL, GLFW


import sys, os, math

try: # PyOpenGL
  from OpenGL.GL import *
except:
  print( 'Error: PyOpenGL has not been installed.' )
  sys.exit(0)

try: # GLFW
  import glfw
except:
  print( 'Error: GLFW has not been installed.' )
  sys.exit(0)



# Globals

window = None

windowWidth  = 1000 # window dimensions
windowHeight = 1000

minX = None # range of points
maxX = None
minY = None
maxY = None

r  = 0.01 # point radius as fraction of window size

numAngles = 32
thetas = [ i/float(numAngles)*2*3.14159 for i in range(numAngles) ] # used for circle drawing

allPoints = [] # list of points

lastKey = None  # last key pressed

discardPoints = False
addPauses = True

# Point
#
# A Point stores its coordinates and pointers to the two points beside
# it (CW and CCW) on its hull.  The CW and CCW pointers are None if
# the point is not on any hull.
#
# For debugging, you can set the 'highlight' flag of a point.  This
# will cause the point to be highlighted when it's drawn.

class Point(object):

    def __init__( self, coords ):

      self.x = float( coords[0] ) # coordinates
      self.y = float( coords[1] )

      self.ccwPoint = None # point CCW of this on hull
      self.cwPoint  = None # point CW of this on hull

      self.highlight = False # to cause drawing to highlight this point


    def __repr__(self):
      return 'pt(%g,%g)' % (self.x, self.y)


    def drawPoint(self):

      # Highlight with yellow fill
      
      if self.highlight:
          glColor3f( 0.9, 0.9, 0.4 )
          glBegin( GL_POLYGON )
          for theta in thetas:
              glVertex2f( self.x+r*math.cos(theta), self.y+r*math.sin(theta) )
          glEnd()

      # Outline the point
      
      glColor3f( 0, 0, 0 )
      glBegin( GL_LINE_LOOP )
      for theta in thetas:
          glVertex2f( self.x+r*math.cos(theta), self.y+r*math.sin(theta) )
      glEnd()

      # Draw edges to next CCW and CW points.

      if self.ccwPoint:
        glColor3f( 0, 0, 1 )
        drawArrow( self.x, self.y, self.ccwPoint.x, self.ccwPoint.y )

      if self.ccwPoint:
        glColor3f( 1, 0, 0 )
        drawArrow( self.x, self.y, self.cwPoint.x, self.cwPoint.y )



# Draw an arrow between two points, offset a bit to the right

def drawArrow( x0,y0, x1,y1 ):

    d = math.sqrt( (x1-x0)*(x1-x0) + (y1-y0)*(y1-y0) )

    vx = (x1-x0) / d      # unit direction (x0,y0) -> (x1,y1)
    vy = (y1-y0) / d

    vpx = -vy             # unit direction perpendicular to (vx,vy)
    vpy = vx

    xa = x0 + 1.5*r*vx - 0.4*r*vpx # arrow tail
    ya = y0 + 1.5*r*vy - 0.4*r*vpy

    xb = x1 - 1.5*r*vx - 0.4*r*vpx # arrow head
    yb = y1 - 1.5*r*vy - 0.4*r*vpy

    xc = xb - 2*r*vx + 0.5*r*vpx # arrow outside left
    yc = yb - 2*r*vy + 0.5*r*vpy

    xd = xb - 2*r*vx - 0.5*r*vpx # arrow outside right
    yd = yb - 2*r*vy - 0.5*r*vpy

    glBegin( GL_LINES )
    glVertex2f( xa, ya )
    glVertex2f( xb, yb )
    glEnd()

    glBegin( GL_POLYGON )
    glVertex2f( xb, yb )
    glVertex2f( xc, yc )
    glVertex2f( xd, yd )
    glEnd()
      
      

# Determine whether three points make a left or right turn

LEFT_TURN  = 1
RIGHT_TURN = 2
COLLINEAR  = 3

def turn( a, b, c ):

    det = (a.x-c.x) * (b.y-c.y) - (b.x-c.x) * (a.y-c.y)

    if det > 0:
        return LEFT_TURN
    elif det < 0:
        return RIGHT_TURN
    else:
        return COLLINEAR


# Build a convex hull from a set of point
#
# Use the method described in class
def buildHull( points ):

    # Check cases
    if not points:
        
        # No points: return empty hull
        return []

    if len(points) == 3:

        # Base case of 3 points: make a hull
        
        p1, p2, p3 = points[0], points[1], points[2]
        if turn(p1, p2, p3) == LEFT_TURN: #p1 -> p2 -> p3 -> p1 Counterclockwise
            p1.ccwPoint, p2.ccwPoint, p3.ccwPoint = p2, p3, p1
            p1.cwPoint, p2.cwPoint, p3.cwPoint = p3, p1, p2
        elif turn(p1, p2, p3) == RIGHT_TURN: #p1 -> p2 -> p3 -> p1 Clockwise
            p1.ccwPoint, p2.ccwPoint, p3.ccwPoint = p3, p1, p2
            p1.cwPoint, p2.cwPoint, p3.cwPoint = p2, p3, p1
        else:
            p1.ccwPoint, p1.cwPoint = p2, p2
            p3.ccwPoint, p3.cwPoint = p2, p2
            p2.ccwPoint, p2.cwPoint = p1, p3

        pass

    elif len(points) == 2:

        # Base case of 2 points: make a hull
        p1, p2 = points[0], points[1]
        p1.ccwPoint, p2.ccwPoint = p2, p1
        p1.cwPoint, p2.cwPoint = p2, p1

        pass 
    else:

        # Recurse to build left and right hull
        mid = len(points) // 2
        leftHull = points[:mid]
        rightHull = points[mid:]
        buildHull(leftHull)
        buildHull(rightHull)
        
        # You can do the following to help in debugging.  The code
        # below highlights all the points, then shows them, then
        # pauses until you press 'p'.  While paused, you can click on
        # a point and its coordinates will be printed in the console
        # window.  If you are using an IDE in which you can inspect
        # your variables, this will help you to identify which point
        # on the screen is which point in your data structure.
        #
        # This is good to do, for example, after you have recursively
        # built two hulls (above), to see that the two hulls look right.
        #
        # This same highlighting can also be done immediately after you have merged to hulls
        # ... again, to see that the merged hull looks right.

        for p in points:
            p.highlight = True
        display(wait=addPauses)

        # Merge the two hulls
        mergeHulls(leftHull, rightHull)
        pass

        # Pause to see the result, then remove the highlighting from
        # the points that you previously highlighted:

        display(wait=addPauses)
        for p in points:
            p.highlight = False
        
        

    # At the very end of buildHull(), you should display the result
    # after every merge, as shown below.  This call to display() does
    # not pause.
    
    display()
    
    
# Merge two hulls
def mergeHulls(left, right):
    
    # Find the upper and lower tangents by calling respective functions
    upperLeft, upperRight = upperTangent(left, right)
    lowerLeft, lowerRight = lowerTangent(left, right)
    
    # Connect the upper and lower tangents to form the final hull by setting pointers
    upperLeft.cwPoint = upperRight
    upperRight.ccwPoint = upperLeft
    lowerLeft.ccwPoint = lowerRight
    lowerRight.cwPoint = lowerLeft
    
    # Global variable that stores the upper left, upper right, lower left and lower right points of the hull used for the tangents
    global hull_final    
    hull_final = [upperLeft, upperRight, lowerLeft, lowerRight]
    

# Algorithm to find the upper tangent, r: left and right point of final tangent line
def upperTangent(left, right):
    
    # Find the leftmost of the right hull and the rightmost point of the left hull
    leftPoint = left[-1]
    rightPoint = right[0]
    
    # Determine if points form a left turn, shift pointer to next point accordingly, "walking" the line up
    while True:
        if turn(leftPoint, rightPoint, rightPoint.cwPoint) == LEFT_TURN:
            rightPoint = rightPoint.cwPoint
            
        elif turn(leftPoint.ccwPoint, leftPoint, rightPoint) == LEFT_TURN:
            leftPoint = leftPoint.ccwPoint
            
        else:
            break
    return leftPoint, rightPoint

# Algorithm to find the lower tangent, r: left and right point of final tangent line
def lowerTangent(left, right):
    # Find the leftmost of the right hull and the rightmost point of the left hull
    leftPoint = left[-1]
    rightPoint = right[0]
    
    # Determine if points form a right turn, shift pointer to next point accordingly, "walking" the line down
    while True:
        if turn(leftPoint, rightPoint, rightPoint.ccwPoint) == RIGHT_TURN:
            rightPoint = rightPoint.ccwPoint
            
        elif turn(leftPoint.cwPoint, leftPoint, rightPoint) == RIGHT_TURN:
            leftPoint = leftPoint.cwPoint
            
        else:
            break
    return leftPoint, rightPoint

# Uses global variables defined earlier to walk through hull and remove pointers of points not in hull
def removePointers(points):
    
    # Global variables from when tangent points were defined and a set for points in hull   
    upL, upR, lowL, lowR = hull_final[0], hull_final[1], hull_final[2], hull_final[3]
    hullPoints = set()

    # Walk through right side of the hull and add points to set
    point = upR
    while point != lowR:
        hullPoints.add(point)
        point = point.cwPoint
    hullPoints.add(lowR)

    # Walk through left side of the hull and add points to set
    point = upL
    while point != lowL:
        hullPoints.add(point)
        point = point.ccwPoint
    hullPoints.add(lowL)

    # Remove pointers of points not in hull
    for point in allPoints:
        if point not in hullPoints:
            point.ccwPoint = None
            point.cwPoint = None

    # Display the final result
    display()
    

windowLeft   = None
windowRight  = None
windowTop    = None
windowBottom = None


# Set up the display and draw the current image

def display( wait=False ):

    global lastKey, windowLeft, windowRight, windowBottom, windowTop
    
    # Handle any events that have occurred

    glfw.poll_events()

    # Set up window

    glClearColor( 1,1,1,0 )
    glClear( GL_COLOR_BUFFER_BIT )
    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

    glMatrixMode( GL_PROJECTION )
    glLoadIdentity()

    glMatrixMode( GL_MODELVIEW )
    glLoadIdentity()

    if maxX-minX > maxY-minY: # wider point spread in x direction
        windowLeft = -0.1*(maxX-minX)+minX
        windowRight = 1.1*(maxX-minX)+minX
        windowBottom = windowLeft
        windowTop    = windowRight
    else: # wider point spread in y direction
        windowTop    = -0.1*(maxY-minY)+minY
        windowBottom = 1.1*(maxY-minY)+minY
        windowLeft   = windowBottom
        windowRight  = windowTop

    glOrtho( windowLeft, windowRight, windowBottom, windowTop, 0, 1 )

    # Draw points and hull

    for p in allPoints:
        p.drawPoint()

    # Show window

    glfw.swap_buffers( window )

    # Maybe wait until the user presses 'p' to proceed
    
    if wait:

        sys.stderr.write( 'Press "p" to proceed ' )
        sys.stderr.flush()

        lastKey = None
        while lastKey != 80 and lastKey != glfw.KEY_ESCAPE: # wait for 'p'
            glfw.wait_events()
            display()

        sys.stderr.write( '\r                     \r' )
        sys.stderr.flush()

        if lastKey == glfw.KEY_ESCAPE:
            sys.exit(0)

    

# Handle keyboard input

def keyCallback( window, key, scancode, action, mods ):

    global lastKey
    
    if action == glfw.PRESS:
        lastKey = key



# Handle window reshape


def windowReshapeCallback( window, newWidth, newHeight ):

    global windowWidth, windowHeight

    windowWidth  = newWidth
    windowHeight = newHeight



# Handle mouse click/release

def mouseButtonCallback( window, btn, action, keyModifiers ):

    if action == glfw.PRESS:

        # Find point under mouse

        x,y = glfw.get_cursor_pos( window ) # mouse position

        wx = (x-0)/float(windowWidth)  * (windowRight-windowLeft) + windowLeft
        wy = (windowHeight-y)/float(windowHeight) * (windowTop-windowBottom) + windowBottom
        minDist = windowRight-windowLeft
        minPoint = None
        for p in allPoints:
            dist = math.sqrt( (p.x-wx)*(p.x-wx) + (p.y-wy)*(p.y-wy) )
            if dist < r and dist < minDist:
                minDist = dist
                minPoint = p

        # print point and toggle its highlight

        if minPoint:
            minPoint.highlight = not minPoint.highlight
            print( minPoint )

        
    
# Initialize GLFW and run the main event loop

def main():

    global window, allPoints, minX, maxX, minY, maxY, r, discardPoints, addPauses
    
    # Check command-line args

    if len(sys.argv) < 2:
        print( 'Usage: %s filename' % sys.argv[0] )
        sys.exit(1)

    args = sys.argv[1:]
    while len(args) > 1:
        if args[0] == '-d':
            discardPoints = True
        elif args[0] == '-np':
            addPauses = False
        args = args[1:]

    # Set up window
  
    if not glfw.init():
        print( 'Error: GLFW failed to initialize' )
        sys.exit(1)

    window = glfw.create_window( windowWidth, windowHeight, "Assignment 1", None, None )

    if not window:
        glfw.terminate()
        print( 'Error: GLFW failed to create a window' )
        sys.exit(1)

    glfw.make_context_current( window )
    glfw.swap_interval( 1 )
    glfw.set_key_callback( window, keyCallback )
    glfw.set_window_size_callback( window, windowReshapeCallback )
    glfw.set_mouse_button_callback( window, mouseButtonCallback )

    # Read the points

    with open( args[0], 'rb' ) as f:
      allPoints = [ Point( line.split(b' ') ) for line in f.readlines() ]

    # Get bounding box of points

    minX = min( p.x for p in allPoints )
    maxX = max( p.x for p in allPoints )
    minY = min( p.y for p in allPoints )
    maxY = max( p.y for p in allPoints )

    # Adjust point radius in proportion to bounding box
    
    if maxX-minX > maxY-minY:
        r *= maxX-minX
    else:
        r *= maxY-minY

    # Sort by increasing x.  For equal x, sort by increasing y.
    
    allPoints.sort( key=lambda p: (p.x,p.y) )

    # Run the code
    #
    # Updated this to remove pointers of points not on the hull after hull function has been called
    removePointers(buildHull( allPoints ))
    
    # Wait to exit

    while not glfw.window_should_close( window ):
        glfw.wait_events()
        if lastKey == glfw.KEY_ESCAPE:
            sys.exit(0)

    glfw.destroy_window( window )
    glfw.terminate()
    


if __name__ == '__main__':
    main()
