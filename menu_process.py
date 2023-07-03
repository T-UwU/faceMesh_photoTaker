import cv2
import numpy as np
import mediapipe as mp


def video(cap, debug):
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

    success, image = cap.read()
    direction = "Empty"

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = face_mesh.process(image)
    image.flags.writeable = True

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    img_h, img_w, img_c = image.shape
    face_3d = []
    face_2d = []

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx, lm in enumerate(face_landmarks.landmark):
                if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                    if idx == 1:
                        nose_2d = (lm.x * img_w, lm.y * img_h)

                    x, y = int(lm.x * img_w), int(lm.y * img_h)

                    face_2d.append([x, y])
                    face_3d.append([x, y, lm.z])

            # Convert it to NumPy array
            face_2d = np.array(face_2d, dtype=np.float64)
            face_3d = np.array(face_3d, dtype=np.float64)

            # The camera matrix
            focal_length = 1 * img_w
            cam_matrix = np.array([[focal_length, 0, img_h / 2],
                                   [0, focal_length, img_w / 2],
                                   [0, 0, 1]])

            # The distortion parameters
            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            # Solve PnP
            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

            # Get rotational matrix
            rmat, jac = cv2.Rodrigues(rot_vec)
            # Get angles
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
            # Get the y rotation degree
            x = angles[0] * 360
            y = angles[1] * 360
            z = angles[2] * 360

            # See where the user's head is tilting
            if y < -10:
                direction = "Left"
            elif y > 10:
                direction = "Right"
            elif x < -10:
                direction = "Down"
            elif x > 10:
                direction = "Up"
            else:
                direction = "Forward"

            # Display nose direction
            if debug:
                p1 = (int(nose_2d[0]), int(nose_2d[1]))
                p2 = (int(nose_2d[0] + y * 15), int(nose_2d[1] - x * 5))

                cv2.line(image, p1, p2, (255, 0, 0), 2)

                # Add the text on the image
                cv2.putText(image, direction, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)
                cv2.putText(image, "x: " + str(np.round(x, 2)), (img_w - 150, 25), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0),
                            2)
                cv2.putText(image, "y: " + str(np.round(y, 2)), (img_w - 150, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0),
                            2)
                cv2.putText(image, "z: " + str(np.round(z, 2)), (img_w - 150, 75), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0),
                            2)

        if debug:
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec)

    return [image, direction]