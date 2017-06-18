from kivy.gesture import GestureDatabase
from kivy.uix.floatlayout import FloatLayout
from kivy.gesture import Gesture

gesture_strings = {
    'right_to_left_line': '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',
    'left_to_right_line': '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',
    'wheel_up_to_down': 'eNptjj1uwkAQhZfwb0j4TbiC03CFuNs2Es02FjJmhC0Sm7deh1BYSppIOQLchI6jMTYWNEwxM3rz3uj7qfrr8Gs3XVFiUk2WLCfE6y8qGR5sVRNCRN4noap4E6ipBo+AwlVgUJeiLFXntg2XJkDjJva4lb/nGx0vU9+g+a/aLJv4g7QX+YSWfDvu8zqoJh8So+M1JWi7sO7SzQqDhQ4zdjM82gXRJg4jk+DJRe9u6j2/W+hzaJBhaKsKh3YYScc4F9hc+MZYOttTIaQLT3VzIF8TReX/ZxcvV8c1+4eJx/Z0MT0Du5Ne2Q==',
    'wheel_down_to_up': 'eNprYE7Oziyr1EtPLS4pLUrlcofShQyajYWMtYVMGhEsDAwMeYm5qYXMEUAWQyFLBBuQykjNTM8oKWR1Z4CCCFYgUZ6ZUpJRyIYQ5AcSULPjC4ryU0qTSwrZOyM4gcIl+TmpRYl5yamFHO72O2eCwKwIdqBEcUlRfnZqcSFnbCEXVtcFgxVwFXID3chTW8irAXZRQX5mXklxIV9sIT9WXQEgea5CAaAmwdpCIY0IRqCmykJhd4eiCRDHggQqCkXcHaoegAVKkxIjeEAOSi5KTc2Dmi8aWygGVwHX21YonghUXpqkBwDjGV+7',
    'up_to_down_line': 'eNpt1X9M1GUcwPEjBBQsECLJElDSjuRXVog/6r5l9qUsOlPpK4nCwVeOgOM+x51A8cChSSSSgGkCUYRGtlwx4g+0TSA2Qwcb01LmbLF0y35NWq3JqNn3np7P9mkP9wccr3vfj+fzPPfF659XVLi7MqlAL3N7XHqwKn6DKb4W/BjcYdZCTSaTeHin01Wa78lzg7+qBGRtV5U1f2qBxsN2vbDA7oY5qpKrmHw3bY7xw5FbokOA5vsbArUg41eZ21VapJdBUDbMnfV9N/MgGOYZ7x7MIMTMX95ZWuhwl8H8bLjTPOvTrL4gGO4ynhXKIMys+RnPqoQFqmWydyyrt36UQwWEq5YtgR0dqV6Tx2b31REM7jbbje77iJmE6EMVdqmIZHAPL65u7Ir9JzldLhYyiOLFlR897cUszSgGKk6eCi36AYt7GSzixcThS+HLbkfJxX0M7ufFpdNTwad33ZKLxQyiefFt5vC++L4JuYhhEMuLiwFxM9dS++ViCYOlvBhfd35q6EK9XMQxeIAXo8PnLpx0j8vFMgbLeXFuxvl1Q1iPXDzIwMyLsxuO938x6ZSLeAYP8WKoS+9efj1FLlYwSOBFf1xBzMiqTnnqiQySeNFX0h72e1COXCQzSOFFd8bqy58tHvQVtZr/Tf9mLB5msJIXR7Z9mrlpkclXNC1si0yJx+IRBo/6ioFGb1tVYvMsxWMMUnnxyW9Lf7JsVeRiFYM0XvTZ4lsyQmLlYjWDNbz4cmzo87+LvHKxlsE6Xny1P+bnhpVh8loeZ/AEL85afpm22axyYWGg8OL8tRUhN3d0ysWTDJ7ixeiZBRFZfw3K+7KewdO8GO85Ef7HtFcuNjB4hhcXK/2iI7NnOR8qg3RefPNd4rHu0BG5eJbBc7y4nDSW8GvjDbnYyOB5Xky0TPcyxSQXLzDI4MWV661rh8/McsZeZGDlxdWBmvXJmcr/Cl2b77te5bl03SEuP5uy4SWzqpRb+RVOVfZ08jt1sJniUYFbKDYJ3EqxQmAmRbvAlynmCNQopgvcRjFNYJaBCmKKwFcoxgrcTjFKYDbFuQJ3EKy9JXAnxRsCcyhOCsylOC7QRrFfYB7FEwLzKeLkdYo45F0UccgFFJ0C7RQ1gYUUrQJfpagILKKIQy6miEMuoRgm0EERh1xK0STQSdCLkweKUwJd5DB4cfJlFEcEuini5D0UewTupoiTLzcwBxEnX2GgExEnX0kRj/drFPF4v04RJ19FEc88o4hnvpqiWWANRdwOL0XcjlqKuB17CNbc5rc62EsRh/wGRX68/epgH0WcZx0ZXY1X4JsUce31FPHUvUURV7SfIq6ogWA1npAD5NhU49ewkeKg+PBvU8QPf5DiQTGQJoq4omaKOeI1WyjiMg9RxBW9QxG/CIcJMlzREYq4He9SHBR4lCKe5FaKeJLbKOLlop2iVazoPYq4Rx0UY8SU3qeIe/QBRVxmJ8EqXNGHFHHjuigOiDc6RhE37jhFXPtHuseWq80z7rtLi3VXriNPh27VcqrVd2vTAowHygvz3Xb4WFX++0oY/xqT/gU38Wlk'
}

#This database can compare gestures the user makes to its stored     gestures
#and tell us if the user input matches any of them.
gestures = GestureDatabase()
for name, gesture_string in gesture_strings.items():
    gesture = gestures.str_to_gesture(gesture_string)
    gesture.name = name
    gestures.add_gesture(gesture)


class GestureBox(FloatLayout):

    def __init__(self, **kwargs):
        for name in gesture_strings:
            self.register_event_type('on_{}'.format(name))
        super(GestureBox, self).__init__(**kwargs)

    def on_left_to_right_line(self):
        pass

    def on_right_to_left_line(self):
        pass

    def on_wheel_up_to_down(self):
        pass

    def on_wheel_down_to_up(self):
        pass

    def on_up_to_down_line(self):
        pass

#To recognize a gesture, you’ll need to start recording each individual event in the
#touch_down handler, add the data points for each call to touch_move , and then do the
#gesture calculations when all data points have been received in the touch_up handler.

    def on_touch_down(self, touch):
        #create an user defined variable and add the touch coordinates
        touch.ud['gesture_path'] = [(touch.x, touch.y)]
        super(GestureBox, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        try:
            touch.ud['gesture_path'].append((touch.x, touch.y))
        except KeyError as e:
            print(e)
        super(GestureBox, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        try:
            if 'gesture_path' in touch.ud:
            #create a gesture object
                gesture = Gesture()
            #add the movement coordinates
                gesture.add_stroke(touch.ud['gesture_path'])
            #normalize so thwu willtolerate size variations
                gesture.normalize()
            #minscore to be attained for a match to be true
                match = gestures.find(gesture, minscore=0.7)
                if match:
                    self.dispatch('on_{}'.format(match[1].name))
        except KeyError as e:
            print('Gestures error')
        super(GestureBox, self).on_touch_up(touch)