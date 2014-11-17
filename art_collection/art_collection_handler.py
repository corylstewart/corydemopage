from EnhancedHandler import EnhancedHandler as EH
from my_email_classes import email_sender as EMS
import art_collection_db as ACDB
from google.appengine.ext import ndb
#from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
import urllib
import time


class AddToDatabaseHandler(EH.EnhancedHandler):
    def get(self):
        #self.arg_dict['upload_url'] = blobstore.create_upload_url('/upload')
        self.render('add_art_to_database.html', **self.arg_dict)

    def post(self):
        self.arg_dict['piece_title'] = self.request.get('piece_title')
        self.arg_dict['piece_artist'] = self.request.get('piece_artist')
        self.arg_dict['piece_location'] = self.request.get('location_selection_hidden')
        self.arg_dict['piece_medium'] = self.request.get('medium_selection_hidden')
        self.arg_dict['piece_purchase_price'] = self.request.get('piece_purchase_price')
        self.arg_dict['piece_value'] = self.request.get('piece_value')
        self.arg_dict['piece_value_app'] = self.request.get('piece_value_app') #what is this
        self.arg_dict['piece_app'] = self.request.get('piece_app')
        self.arg_dict['app_or_est'] = self.request.get('app_selection_hidden')
        upload_files = self.request.POST['file_to_upload']
        self.arg_dict['piece_description'] = self.request.get('piece_description')
        art = ACDB.ArtWork()
        #old stuff
        art.title = self.arg_dict['piece_title']
        art.artist = self.arg_dict['piece_artist']
        art.location = self.arg_dict['piece_location']
        art.medium = self.arg_dict['piece_medium']
        art.purchase_price = self.arg_dict['piece_purchase_price']
        art.value = self.arg_dict['piece_value']
        art.appraised_by = self.arg_dict['piece_app']
        art.app_or_est = self.arg_dict['app_or_est']
        art.description = self.arg_dict['piece_description']
        try:
            art.photo = upload_files.value
            art.clean_photo()
            art.user = self.user
            key = art.put()
            if key:
                EMS.AdminAlertEmail().send_new_picure_upload()      ###new line to send emails
                #self.arg_dict['success_message'] = 'Your entry has been saved.  Clear form to enter another piece'
                self.redirect('/edit/' + (str(key).split()[1][:-1]))   ###new redirect to edit page rather than back to add page
            else:
                self.arg_dict['piece_artist'] = 'There was an error please try again!'
        except:
            self.arg_dict['piece_artist'] = 'Please Select a file'
        self.render('add_art_to_database.html', **self.arg_dict)


class ImgHandler(EH.EnhancedHandler):
    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(art.photo)

class ThumbHandler(EH.EnhancedHandler):
    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(art.thumb_nail)

class ScaledHandler(EH.EnhancedHandler):
    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(art.scaled_photo)

class CollectionHandler(EH.EnhancedHandler):
    def get(self):
        q = ACDB.ArtWork().query(ACDB.ArtWork.user == self.user)
        self.arg_dict['art_works'] = []
        i = 0
        for work in q:
            self.arg_dict['art_works'].append(work)
            i +=1
            if i == 30:
                break
        self.render('show_art.html', **self.arg_dict)

    def post(self):
        self.arg_dict['piece_location'] = self.request.get('location_selection_hidden')
        self.arg_dict['piece_medium'] = self.request.get('medium_selection_hidden')
        self.arg_dict['piece_sorting'] = self.request.get('sort_selection_hidden')
        q = ACDB.ArtWork().collection_page_query(self.user,
                                                 self.arg_dict['piece_location'],
                                                 self.arg_dict['piece_medium'],
                                                 self.arg_dict['piece_sorting'])
        self.arg_dict['art_works'] = []
        i = 0
        for work in q:
            self.arg_dict['art_works'].append(work)
            i +=1
            if i == 30:
                break

        self.render('show_art.html', **self.arg_dict)


class PieceEditHandler(EH.EnhancedHandler):
    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        if self.user != art.user:
            self.write("Users do not match")
            return
        self.arg_dict['work'] = art
        stuff_dict= {'piece_title' : art.title,
                     'piece_artist' : art.artist,
                    'piece_location' : art.location,
                    'piece_medium' : art.medium,
                    'piece_purchase_price' : art.purchase_price,
                    'piece_value' : art.value,
                    'piece_value_app' : art.app_or_est,
                    'piece_app' : art.appraised_by,
                    'piece_description' : art.description}
        for key,value in stuff_dict.items():
            if value:
                self.arg_dict[key] = value
            else:
                self.arg_dict[key] = ''
        self.render('add_art_to_database.html', **self.arg_dict)

    def post(self, resource):
        resource = int(urllib.unquote(resource))
        hidden_resource = int(self.request.get('hidden_key'))
        if resource != hidden_resource:
            self.write("Keys don't match.")
            return
        art = ACDB.ArtWork().get_by_id(resource)
        if art.user != self.user:
            self.write("Users do not match")
            return
        art.title = self.request.get('piece_title')
        art.artist = self.request.get('piece_artist')
        art.location = self.request.get('location_selection_hidden')
        art.medium = self.request.get('medium_selection_hidden')
        art.purchase_price = self.request.get('piece_purchase_price')
        art.value = self.request.get('piece_value')
        art.app_or_est = self.request.get('app_selection_hidden')
        art.appraised_by = self.request.get('piece_app')
        art.description = self.request.get('piece_description')
        upload_files = self.request.POST['file_to_upload']
        if upload_files != '':
            try:
                art.photo = upload_files.value
                art.clean_photo()
            except:
                pass
        #self.write(len(art.photo))
        art.put()
        self.redirect('/edit/'+str(resource))