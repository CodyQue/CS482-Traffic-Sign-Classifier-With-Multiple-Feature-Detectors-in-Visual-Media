import violajones
import cv2
import numpy as np
import pandas as pd
import featureselector
    
# This function is used to extract traffic sign features and classify them. This returns two DataFrames: the 4 Haar Features of
# each feature, and the classification DataFrame.
def trainSigns(size = 400):
    
    trainRed = pd.DataFrame(columns=['Aba Boost 1', 'Aba Boost 2', 'Aba Boost 3', 'Aba Boost 4'])
    signsRed = pd.DataFrame(columns=['Signs'])
    
    trainYellow = pd.DataFrame(columns=['Aba Boost 1', 'Aba Boost 2', 'Aba Boost 3', 'Aba Boost 4'])
    signsYellow = pd.DataFrame(columns=['Signs'])
    
    train = pd.DataFrame(columns=['Aba Boost 1', 'Aba Boost 2', 'Aba Boost 3', 'Aba Boost 4'])
    signs = pd.DataFrame(columns=['Signs'])
    
    with open("signs.txt", "r") as file:
        for i in file:
            fileNameArr = i.rstrip().split(" ")
            #print(fileNameArr)
            signName = "signs/" + fileNameArr[0] + ".png"
            
            image = cv2.imread(signName) 
            image = cv2.resize(image, (size, size))
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            imageWithFeatures, features = featureselector.selectFeaturesFromImage(image)
            integralImage = violajones.calculateIntegralImage(image)
            
            blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                featuresInSigns = []
                area = cv2.contourArea(contour)
                if area > 10000:
                    #print('Area: ', area)
                    
                    epsilon = 0.03 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    # Selects features inside of the big shape
                    point_size=1
                    for f in features:
                        x, y = f
                        tuplePoint = (float(f[1]), float(f[0]))
                        determine = cv2.pointPolygonTest(contour, tuplePoint, measureDist=False)
                        if (determine >= 0):
                            featuresInSigns.append(f)
                            #cv2.circle(image, (y, x), point_size, (255, 0, 0), -1)
                           
                    # Determines the color of the sign. 
                    mask = np.zeros_like(image)
                    cv2.drawContours(mask, [contour], -1, (255, 255, 255), thickness=cv2.FILLED)
                    shape_colors = cv2.bitwise_and(image, mask)
                    color_list = shape_colors.reshape(-1, 3)
                    unique_colors = np.unique(color_list, axis=0)
                    
                    yellow_present = False
                    red_present = False
                    
                    for color in unique_colors:
                        # Checks if the color is yellow
                        if color[2] > 150 and color[1] > 150 and color[0] < 100 and yellow_present == False:
                            print('There is yellow')
                            yellow_present = True
            
                    ababoostfeatures = violajones.computeHaarFeatures(integralImage, featuresInSigns, gray_image)
                    
                    #Obtains the sign classifiers from the .txt file
                    count = int(fileNameArr[1])
                    df = pd.DataFrame({'Signs': [int(count)] * len(ababoostfeatures)})
                        
                    if yellow_present == True:
                        trainYellow = pd.concat([train, ababoostfeatures], ignore_index=True)
                        signsYellow = pd.concat([signs, df], ignore_index=True)    
                    if (red_present == False) and (yellow_present == False):
                        print('ELSE: ', fileNameArr[0])
                        train = pd.concat([train, ababoostfeatures], ignore_index=True)
                        signs = pd.concat([signs, df], ignore_index=True)
                    #print(signName)
                    #print(ababoostfeatures)

                    #cv2.imshow("Shapes Detected", image)
                    #cv2.waitKey(0)
                    #cv2.destroyAllWindows()
                    #print(signs)
                    
        train.to_csv('train.csv', index=False)
        signs.to_csv('trainClassifier.csv', index=False)       
        trainYellow.to_csv('trainYellow.csv', index=False)
        signsYellow.to_csv('trainClassifierYellow.csv', index=False)
    
trainSigns()
print('Done With Training And Classifying Signs. Check directory for .csv files.')