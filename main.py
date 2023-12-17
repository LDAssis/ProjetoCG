from ultralytics import YOLO
from Person import Person
from Area import Area
import numpy as np
import cv2
model = YOLO("yolov8x.pt")

countSaveImages = 0

areas = []
#points = np.array([[266,8],[89,139],[97,517]
#                ,[267,537],[474,328],[465,149]
#                ,[306,113],[319,29]
#                   ])
points = np.array([[469,147],[773,154],[768,323]
                ,[470,315]
                   ])
pts = points.reshape(-1,1,2)
areas.append(Area(pts, "SECURE", (0,0,255)))

#points = np.array([[468,119],[492,2],[522,2]
#                ,[507,81],[518,83],[587,317]
#                ,[497,310],[489,328]
#                   ])
points = np.array([[471,339],[809,340],[816,407]
                ,[470,401],
                   ])
pts = points.reshape(-1,1,2)
areas.append(Area(pts, "INVASION", (255,0,0)))

sensi = 3 #Smaller less sensitive

vid = cv2.VideoCapture("shoppingTest2.mp4")

idControl = 1 #Control persons id

persons = [] #Persons history list

def findPeople(centerX, centerY, width, height):
    global idControl
    if (len(persons) >= 1):
        for person in persons:
            if person.isMe(centerX, centerY):
                    person.attPos(centerX, centerY)
                    person.timeoutPerson = 0 #Reset timeout count
                    person.sensiH = height/sensi #Calcula a sensibilidade com base no tamanho da box, quanto maior a box, maior tolerancia
                    person.sensiW = width/sensi  # Calcula a sensibilidade com base no tamanho da box, quanto maior a box, maior tolerancia
                    return (int) (person.id)
    return 0

def addExcludeAllTimeout():
    for person in persons:
        person.addTimeout()
        if person.timeoutPerson > 10:
            persons.remove(person)

def drawRotes(image):
    for pers in persons:
        for i in range(0, len(pers.historyX)):
            image = cv2.circle(image, (pers.historyX[i],pers.historyY[i]), 2, pers.color, thickness=5)


def drawAreas(image):
    for area in areas:
        img_poly = cv2.polylines(image, [area.points], isClosed=True, color=area.color, thickness=2)


def verifyInvade():
    for area in areas:
        for person in persons:
            dentro_area = cv2.pointPolygonTest(area.points, (person.centerX, person.centerY), True) >= 0
            if dentro_area:
                if area.type == "INVASION":
                    if person.isSecure == False:
                        person.isInvasion = True
                else:
                    person.isSecure = True
                    if person.isInvasion == True:
                        person.isSecure = True
                        person.color = (255,0,0)




def createPeople(x,y, width, height):
    global idControl
    persons.append(Person(idControl, x, y, width/sensi, height/sensi))
    idControl = idControl + 1

while(True):
    #Capture image video or camera
    ret, frame = vid.read()

    #Convert to RGB, by default opencv load images ins BGR
    #Its maybe cause conflicts during inference image if image is in BGR
    image_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #Do the inference
    predict = model(image_RGB)

    for obj in predict[0].boxes:
        if obj.cls[0] == 0:#cls 0 == person
            x = (int) (obj.xyxy[0][0])
            y = (int) (obj.xyxy[0][1])
            x2 = (int) (obj.xyxy[0][2])
            y2 = (int) (obj.xyxy[0][3])
            conf = (int) (obj.conf[0]*100)

            centerX = (int) (obj.xywh[0][0])
            centerY = (int)(obj.xywh[0][1])
            width = (int)(obj.xywh[0][2])
            height = (int)(obj.xywh[0][3])

            personID = findPeople(centerX, centerY, width, height)
            if personID != 0:
                for per in persons:
                    if per.id == personID:
                        cv2.rectangle(image_RGB, (x, y), (x2, y2), per.color, 2)
                        if per.isInvasion and per.isSecure:
                            cv2.putText(image_RGB, str(personID) + " SUSPECT", (x, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                        per.color, 2,
                                        cv2.LINE_AA, False)
                        else:
                            cv2.putText(image_RGB, str(personID) + " P ", (x, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                        per.color, 2,
                                        cv2.LINE_AA, False)

            else:
                createPeople(centerX, centerY, width, height)
                cv2.rectangle(image_RGB, (x, y), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image_RGB, str(idControl-1) + " P ", (x, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 0), 2,
                            cv2.LINE_AA, False)

    cv2.putText(image_RGB, "Count: "+str(len(persons)), (0,30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 0, 255), 2,
                cv2.LINE_AA, False)
    addExcludeAllTimeout()
    drawRotes(image_RGB)
    drawAreas(image_RGB)
    verifyInvade()


    #Plot image for debug
    #image_RGB = predict[0].plot()

    #Converts back the image to BGR to be able to view
    image_BGR = cv2.cvtColor(image_RGB, cv2.COLOR_RGB2BGR)

    #image_BGR = cv2.resize(image_BGR, (1600, 900), interpolation=cv2.INTER_LINEAR)

    #Show image
    cv2.imshow('Image', image_BGR)

    #if cv2.waitKey(1) & 0xFF == ord('s'):
    #    cv2.imwrite(str(countSaveImages)+"image.png", image_BGR)
    #    countSaveImages = countSaveImages+1

    #Wait for 1ms for key "q" pressure to end the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()