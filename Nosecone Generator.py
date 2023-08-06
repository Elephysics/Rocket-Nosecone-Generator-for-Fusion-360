#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback 
import math
import numpy



def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        des = adsk.fusion.Design.cast(app.activeProduct)
        root = des.rootComponent
        
        # Create a new sketch.
        sk = root.sketches.add(root.xYConstructionPlane)
        lines = sk.sketchCurves.sketchLines
        arcs = sk.sketchCurves.sketchArcs


#**********User editable start**********

        #Units in cm
        NoseConeType = "Haack"      #Haack, Conic, BluntConic, Elliptical, Parabolic, Ogive, BluntOgive
        BASE_DIAMETER = 4.13
        LENGTH = 15
        NoseRadius = .4 #For Blunt Ogive and Blunt Conic

        Numpnts = 100   #Number of points to have in spline
        C = 0 #Haack Series type    LD-Haack (Von Karman) = 0, LV-Haack = .33, Tangent = .66
        K = 1 #Parabola type cone = 0, Half = .5, Three Quarter = .75, Full = 1

#**********User editable end**********

        r = BASE_DIAMETER/2
        pnts = adsk.core.ObjectCollection.create()
        x = numpy.linspace(0, LENGTH, Numpnts)
        if NoseConeType == "Haack":
            theta = numpy.arccos(1-2*x/LENGTH)
            y = 2 * (r/numpy.sqrt(numpy.pi)) * numpy.sqrt(theta - numpy.sin(2*theta)/2 + C * numpy.power(numpy.sin(theta),3))
            for i in range(Numpnts):           
                pnts.add(adsk.core.Point3D.create(x[i],y[i],0))
                

        if NoseConeType == "Conic":
            y = (x*r)/LENGTH
            for i in range(Numpnts):                     
                pnts.add(adsk.core.Point3D.create(x[i],y[i],0))
                

        if NoseConeType == "Elliptical":
            y = r*numpy.sqrt(1-(numpy.power(x,2)/numpy.power(LENGTH,2)))
            for i in range(Numpnts):                       
                pnts.add(adsk.core.Point3D.create(numpy.flip(x)[i],y[i],0))


        if NoseConeType == "Parabolic":
            y = r*((2*(x/LENGTH)-K*(numpy.power((x/LENGTH),2)))/(2-K))
            for i in range(Numpnts):                       
                pnts.add(adsk.core.Point3D.create(x[i],y[i],0))


        if NoseConeType == "Ogive":
            p = (numpy.power(r,2)+numpy.power(LENGTH,2))/(2*r)
            y = numpy.sqrt(numpy.power(p,2)-numpy.power((LENGTH-x),2))+r-p
            for i in range(Numpnts):                       
                pnts.add(adsk.core.Point3D.create(x[i],y[i],0))


        if NoseConeType == "BluntOgive":
            p = (numpy.power(r,2)+numpy.power(LENGTH,2))/(2*r)
            xo = LENGTH - numpy.sqrt(numpy.power((p-NoseRadius),2)-numpy.power((p-r),2))
            xa = xo - NoseRadius
            yt = (NoseRadius*(p-r))/(p-NoseRadius)
            xt = xo - numpy.sqrt(numpy.power(NoseRadius,2)-numpy.power(yt,2))
            sweepAngle = numpy.arcsin(yt/NoseRadius)
            x = numpy.linspace(xt, LENGTH, Numpnts)            
            startPoint = adsk.core.Point3D.create(xa, 0, 0)
            centerPoint = adsk.core.Point3D.create(xo, 0, 0)
            arcs.addByCenterStartSweep(centerPoint, startPoint, -sweepAngle)
            y = numpy.sqrt(numpy.power(p,2)-numpy.power((LENGTH-x),2))+r-p   
            for i in range(Numpnts):                    
                pnts.add(adsk.core.Point3D.create(x[i],y[i],0))


        if NoseConeType == "BluntConic":
            xt = (numpy.power(LENGTH,2)/r)*numpy.sqrt(numpy.power(NoseRadius,2)/(numpy.power(r,2)+numpy.power(LENGTH,2)))
            yt = (xt*r)/LENGTH
            xo = xt + numpy.sqrt(numpy.power(NoseRadius,2)-numpy.power(yt,2))
            xa = xo -NoseRadius
            sweepAngle = numpy.arcsin(yt/NoseRadius)
            x = numpy.linspace(xt, LENGTH, Numpnts)            
            startPoint = adsk.core.Point3D.create(xa, 0, 0)
            centerPoint = adsk.core.Point3D.create(xo, 0, 0)
            arcs.addByCenterStartSweep(centerPoint, startPoint, -sweepAngle)
            y = (x*r)/LENGTH 
            for i in range(Numpnts):                    
                pnts.add(adsk.core.Point3D.create(x[i],y[i],0))


        sk.sketchCurves.sketchFittedSplines.add(pnts)
        
        axisLine = lines.addByTwoPoints(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(x[i], 0, 0)) 
        lines.addByTwoPoints(adsk.core.Point3D.create(x[i], 0, 0), adsk.core.Point3D.create(x[i], numpy.max(y), 0)) 
        


        prof = sk.profiles.item(0)

        # Create an revolution input to be able to define the input needed for a revolution
        # while specifying the profile and that a new component is to be created
        revolves = root.features.revolveFeatures
        revInput = revolves.createInput(prof, axisLine, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Define that the extent is an angle of pi to get half of a torus.
        angle = adsk.core.ValueInput.createByReal(2*math.pi)
        revInput.setAngleExtent(False, angle)

        # Create the extrusion.
        ext = revolves.add(revInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))