from onvif import ONVIFCamera
from time import sleep


long_line = ""
for i in range(80):
    long_line += "-"


class Camera:
    def __init__(self, ip, port, login, password):
        #соединение с камерой
        self.my_cam = ONVIFCamera(
            ip,
            port,
            login,
            password
        )

        # Создание медиа сервиса
        self.media_service = self.my_cam.create_media_service()

        
        self.profiles = self.media_service.GetProfiles()
        self.media_profile = self.profiles[0]

        # создание ptz сервиса
        self.ptz = self.my_cam.create_ptz_service()

        
        self.request_absolute_move = self.ptz.create_type("AbsoluteMove")
        self.request_absolute_move.ProfileToken = self.media_profile.token

        self.request_stop = self.ptz.create_type("Stop")
        self.request_stop.ProfileToken = self.media_profile.token

        # создание imaging сервиса
        self.imaging = self.my_cam.create_imaging_service()

        self.request_focus_change = self.imaging.create_type("Move")
        self.request_focus_change.VideoSourceToken = self.media_profile.VideoSourceConfiguration.SourceToken
        
        self.stop()

    # получение позиции камеры
    def get_ptz_position(self):
        status = self.ptz.GetStatus({"ProfileToken": self.media_profile.token})

        print(long_line)
        print("PTZ position: " + str(status.Position))
        print(long_line)

    def get_focus_options(self):
        imaging_status = self.imaging.GetStatus({"VideoSourceToken": self.media_profile.VideoSourceConfiguration.SourceToken})

        print(long_line)
        request = self.imaging.create_type("GetServiceCapabilities")
        imaging_service_capabilities = self.ptz.GetServiceCapabilities(request)

        print("Service capabilities: " + str(imaging_service_capabilities))
        print(long_line)
        print("Imaging status: " + str(imaging_status))
        print(long_line)

    # остановить движение камеры
    def stop(self):
        self.request_stop.PanTilt = True
        self.request_stop.Zoom = True

        self.ptz.Stop(self.request_stop)


    # Absolute move 
    def perform_absolute_move(self):
        self.ptz.AbsoluteMove(self.request_absolute_move)

        sleep(4)

    def move_absolute(self, x, y, zoom):
        print("Moving to: \"" +
              str(x) + ":" + str(y) + ":" + str(zoom) +
              "\""
              )

        status = self.ptz.GetStatus({"ProfileToken": self.media_profile.token})
        status.Position.PanTilt.x = x
        status.Position.PanTilt.y = y
        status.Position.Zoom.x = zoom

        self.request_absolute_move.Position = status.Position

        self.perform_absolute_move()

    # изменение значений фокуса
    def change_focus(self, speed, timeout):
        print("Changing focus with speed: \"" +
              str(speed) +
              "\" and timeout: \"" +
              str(timeout) +
              "\""
              )

        self.request_focus_change.Focus = {
            "Continuous": {
                "Speed": speed
            }
        }

        self.imaging.Move(self.request_focus_change)

        sleep(timeout)

        self.stop()

        sleep(2)
