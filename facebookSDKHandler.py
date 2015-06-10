from kivy.uix.boxlayout import BoxLayout




class FacebookUI(BoxLayout):
    ''' Seems like there was a bug in the kv that wouldn't bind on 
    app.facebook.status, but only on post_status '''

    status_text = StringProperty()
    def __init__(self, **kwargs):
        super(FacebookUI, self).__init__(**kwargs)
        app.bind(facebook=self.hook_fb)
    
    def hook_fb(self, app, fb):
        fb.bind(status=self.on_status)
        app.bind(post_status=self.on_status)
        
    def on_status(self, instance, status):
        self.status_text = \
        'Facebook Status: [b]{}[/b]\nMessage: [b]{}[/b]'.format(
            app.facebook.status, 
            app.post_status)

class FacebookApp(App):
    post_status = StringProperty('-')
    user_infos = StringProperty('-')
    facebook = ObjectProperty()

    def build(self):
        global app
        app = self
        return FacebookUI()