# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User, UserManager
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _

from notebook.notes.constants import *
from notebook.tags.models import Tag_Frame

import datetime


#TODO: refactor out. It is duplicated with the code from notes.models
#from time import gmtime, strftime  
def get_storage_loc(instance, filename):    
    #timepath= strftime('/%Y/%m/%d/')    
    try:
        return 'icons/'+instance.username+'/'+filename   
    except:
        return 'icons/'+instance.name+'/'+filename  #for saving group icon

from django.core.files.storage import FileSystemStorage    
from notebook.env_settings import DB_ROOT
fs = FileSystemStorage(location=DB_ROOT)


class Activation(models.Model):
    #TODO: what is the limit of user username?
    username = models.CharField(max_length=100) 
    activation_id = models.CharField(max_length=100) 
  
    

    

class Member(User):
    ROLE_CHOICES = (        
        ('l', 'learner'),
        ('t', 'teacher'),
        
    )  
    GENDER_CHOICES = (        
        ('f', ugettext_lazy('female')),
        ('m', ugettext_lazy('male')),        
    )    
    LANG_CHOICES = (        
        ('zh-cn', ugettext_lazy('Chinese')),
        ('en-us', ugettext_lazy('English')),        
    )
    DIGEST_CHOICES = (      
        ('n', ugettext_lazy('No Digest')),                
        ('d', ugettext_lazy('Daily Digest')),
        ('w', ugettext_lazy('Weekly Digest')),        
    )  
    PLAN_NOTICE_CHOICES = (      
        ('n', ugettext_lazy('No Notice')),                
        ('y', ugettext_lazy('Receive Plan Notice')),             
    ) 
    HOME_CHOICES = (      
        ('s', ugettext_lazy('Snippets')),                
        ('f', ugettext_lazy('Frames')),
        ('t', ugettext_lazy('Tag Tree')),
        ('a', ugettext_lazy('Add Note Only')),        
    )   
   
    
    nickname = models.CharField(max_length=50, blank=True,  verbose_name=ugettext_lazy('Nickname'))   
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, blank=True) 
    #TODO: change to avatar
    icon = models.ImageField(upload_to=get_storage_loc,blank=True, storage=fs, verbose_name=ugettext_lazy('Icon'))    #TODO:
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name=ugettext_lazy('Gender')) 
    #TODO: change max_length to 5
    #so far, this is only used for scripts instead of in the web app. TODO:
    default_lang = models.CharField(max_length=10, choices=LANG_CHOICES, blank=True,  verbose_name=ugettext_lazy('Default language'))   
    digest = models.CharField(max_length=1, choices=DIGEST_CHOICES, blank=True, default='d',  verbose_name=ugettext_lazy('Digest'))
    plan_notice = models.CharField(max_length=1, choices=PLAN_NOTICE_CHOICES, blank=True, default='y',  verbose_name=ugettext_lazy('Plan Notice')) 
    home = models.CharField(max_length=1, choices=HOME_CHOICES, blank=True, default='s',  verbose_name=ugettext_lazy('Home'))
    #maynot be a good way to do like this. TODO:
    # Use UserManager to get the create_user method, etc.
    objects = UserManager()
    #TODO:
    #timezone = models.CharField(max_length=50, default='Europe/London')
    
    #viewing mode. Later think of adding other viewing modes here so user can set these in their profile
    viewing_private = models.CharField(max_length=20, blank=True)
    default_ui = models.CharField(max_length=20, blank=True,  verbose_name=ugettext_lazy('Default UI'))   
    
    class Meta:
        ordering = ['username']
    
    
    def __unicode__(self): 
        return self.username   
    


    def get_friends(self):
        q1 = Q(friend1=self)
        q2 = Q(friend2=self)
        friend_rels = Friend_Rel.objects.filter(q1 | q2)#TODO: confirmed
        fl = [friend_rel.get_friend(self)  for friend_rel in friend_rels]
        fl.sort(key=lambda r: r.username) 
        return fl
   
   
    def get_friends_names(self):
        friends = self.get_friends()        
        return [friend.username for friend in friends]
       
     
    
    def get_areas(self):
        return Social_Area.objects.filter(owner=self).order_by('name')
       
   
    def get_groups(self):
        return Group.objects.filter(members=self).order_by('name')
    
    
    def get_public_groups(self):
        return Group.objects.filter(members=self, private=False).order_by('name')
    
    
    def is_in_group(self, groupname):
        groups = [group.name for group in self.get_groups()]
        if groupname in groups:
            return True
        else:
            return False
        
    def is_in_groups(self, group_list):
        for group in group_list:
            if self.is_in_group(group):
                return True
            else:
                return False
        
    
    def get_public_snippets_count(self):
        return Social_Snippet.objects.filter(owner=self).count()
        
    def get_public_bookmarks_count(self):
        return Social_Bookmark.objects.filter(owner=self).count()
    
    def get_public_scraps_count(self):
        return Social_Scrap.objects.filter(owner=self).count()
    
    def get_public_frames_count(self):
        return Social_Frame.objects.filter(owner=self).count()
        
    def get_public_notes_count(self):
        return Social_Note.objects.filter(owner=self).count()
  
  
  
#class Member_Settings(models.Model): 
#===============================================================================
#    HOME_CHOICES = (      
#        ('s', ugettext_lazy('Snippets')),                
#        ('f', ugettext_lazy('Frames')),
#        ('t', ugettext_lazy('Tag Tree')),        
#    )   
#    member = models.ForeignKey(Member)
#    home = models.CharField(max_length=1, choices=HOME_CHOICES, blank=True, default='s',  verbose_name=ugettext_lazy('Home')) 
#===============================================================================
    
     
#    def __unicode__(self): 
#        return self.member.username + ugettext_lazy('  settings')   



class Sys_Setting(models.Model):
    USER_REG_CHOICES = (        
        ('y', 'yes'),
        ('n', 'no'),        
    ) 
    user_reg =  models.CharField(max_length=1, choices=USER_REG_CHOICES, blank=True)
    member = models.ForeignKey(Member)
    
       

class Social_Tag(models.Model):    
    name = models.CharField(max_length=150)
    private = models.BooleanField(default=False)
    
    class Meta:
        unique_together = (("name"),)    
        ordering = ['name']
    
    def __unicode__(self):
        return self.name

    
    def name_as_list(self):        
        return self.name.split(':')
    
    #TODO:below not working. Remove
    def get_social_snippet(self):
        return self.social_social_snippet_related.all().count()


#TODO: subclass Note and in dbrouter add allrelation for the two tables
class Social_Note(models.Model):
    owner = models.ForeignKey(Member)
    owner_note_id = models.IntegerField()#reference to the id of the note in the user's db
    title = models.CharField(blank=True, max_length=2000, help_text="The size of the title is limited to 50 characaters.") #maybe 20 is enough
    #event = models.CharField(blank=True,max_length=300)
    desc =  models.TextField(max_length=2000, help_text="The size of the desc is limited to 200 characaters.")
    tags = models.ManyToManyField(Social_Tag, blank=True) #, related_name="%(app_label)s_%(class)s_related" this only works for abstract base class
    #not actually used, just have it here so filters from notes.view can still be used since that note/bookmark/scrap has this field
    private = models.BooleanField(default=False)
    init_date = models.DateTimeField('date created', auto_now_add=True)
    last_modi_date = models.DateTimeField('date last modified', auto_now=True)
    #not actually used, just have it here so filters from notes.view can still be used since that note/bookmark/scrap has this field
    deleted = models.BooleanField(default=False)
    vote =  models.IntegerField(default=0)    
    #attachment = models.FileField(upload_to=get_storage_loc,blank=True, storage=fs)
    
    
    class Meta:
        ordering = ['-init_date','vote','desc','title']
    
    def __unicode__(self):
        return self.desc + u' by ' + self.owner.username
    
    
    def set_translation(self, original_lang, lang, title, desc):
        trans, created =  Social_Note_Translation.objects.get_or_create(note=self)
        trans.original_lang = original_lang
        trans.lang = lang
        trans.title = title
        trans.desc = desc        
        trans.save()
        
    
    
    def get_owner_note(self):
        pass
        

    def get_desc_en(self):
        if not self.get_lang():
            return self.desc
        elif self.get_lang() == 'E':
            return self.desc
        else:
           trans =  Social_Note_Translation.objects.get(note=self)
           return trans.desc 
       
       
    #get the Chinese version   
    def get_desc_cn(self):
        if not self.get_lang():
            return self.desc
        elif self.get_lang() == 'C':
            return self.desc
        else:
           trans =  Social_Note_Translation.objects.get(note=self)
           return trans.desc 
    
    
    def get_title_en(self):
        if not self.get_lang():
            return self.title
        elif self.get_lang() == 'E':
            return self.title
        else:
           trans =  Social_Note_Translation.objects.get(note=self)
           return trans.title 
       
       
    #get the Chinese version   
    def get_title_cn(self):
        if not self.get_lang():
            return self.title
        elif self.get_lang() == 'C':
            return self.title
        else:
           trans =  Social_Note_Translation.objects.get(note=self)
           return trans.title 
          
    
    def get_lang(self):
        if Social_Note_Translation.objects.filter(note=self).exists():
            trans =  Social_Note_Translation.objects.get(note=self)            
            return trans.original_lang
        else:
            return ''

    def get_note_type(self):
        try:
            self.social_snippet
            return 'Snippet'
        except ObjectDoesNotExist:
            try:
                self.social_bookmark
                return 'Bookmark'    
            except ObjectDoesNotExist:
                try:
                    self.social_scrap
                    return 'Scrap'
                except ObjectDoesNotExist:
                    try:
                        self.social_frame
                        return 'Frame'
                    except ObjectDoesNotExist:   
                        log.info('No note type found!')
                        return 'Note' #TODO:
                
    def get_note_bookname(self):        
        return model_book_dict.get(self.get_note_type())
   
   
    def display_tags(self):
        return ','.join([t.name for t in self.tags.filter(private=False).order_by('name')])
    
    def display_all_tags(self):
        return ','.join([t.name for t in self.tags.all().order_by('name')])  
    
    def get_tags(self):
        return [t.name for t in self.tags.filter(private=False).order_by('name')] 
    
    def get_all_tags(self):
        return [t.name for t in self.tags.all().order_by('name')]   
    
    
    #TODO:so far not used yet in the view
    def get_tags_for_group(self, group):
        group_tag_name = group.get_group_tag_name()
        q1 = Q(private=False)
        q2 = Q(name=group_tag_name)
        return [t.name for t in self.tags.filter(q1 | q2).order_by('name').order_by('name')] 
        
        
               

    def get_useful_votes(self):
        votes = Social_Note_Vote.objects.filter(note=self, useful=True)        
        useful_votes = votes.count()
        #print 'useful_votes', useful_votes
        return useful_votes
      
        
    def get_unuseful_votes(self):
        votes = Social_Note_Vote.objects.filter(note=self, useful=False)
        unuseful_votes  = votes.count()
        return unuseful_votes

    def get_total_votes(self):
        votes = Social_Note_Vote.objects.filter(note=self)
        return votes.count()
    
    #TODO: algorithm
    #total*(useful - unuseful)    
    def get_usefulness(self):
        if self.get_useful_votes() or self.get_unuseful_votes():
            return self.get_total_votes()*(self.get_useful_votes() - self.get_unuseful_votes())
        else:
            return 0        


    def get_comments(self):          
        comments = Social_Note_Comment.objects.filter(note=self) 
        return comments 
    
    
    def get_courses(self):          
        courses = Social_Note_Course.objects.filter(note=self) 
        return courses 
    
    
    def get_outer_links(self):          
        backlinks = Social_Note_Backlink.objects.filter(note=self) 
        return backlinks

    
    def get_frame_ids_titles(self):        
        return [[l.id, l.title] for l in self.in_frames.filter(deleted=False)] 
    
    
    
    def is_in_frame(self):
        if self.get_frame_ids_titles():
            return True
        else:
            return False

   
    #TODO: if not using inheritance for reducing the duplicated code, use a shared service provider to do
    # all the similar works. Refacotr.
    #is attachment img?
    def is_img(self):
        file_type = None
        if self.get_note_type() == 'Snippet':
            if self.social_snippet.attachment.name:
                splits = self.social_snippet.attachment.name.split('.') #TODO: if no file type specified
                file_type = splits[len(splits)-1]
        elif self.get_note_type() == 'Frame':
            if self.social_frame.attachment.name:
                splits = self.social_frame.attachment.name.split('.')
                file_type = splits[len(splits)-1]
        
        if file_type in ['jpg','JPG','jpeg','JPEG','png','PNG', 'gif']:
            return True
        else: 
            return False      
   
   
   
    def has_attachment(self):
        if hasattr(self, 'attachment') and self.attachment:
            return True
        return False
    
    
     
     
    def get_relevance(self, tag_path):
        tag_list = tag_path.split('-')
        tag_name = tag_list[-1]
        relevance = 0
        #check if this note really has tag_name as its tag.
        if not tag_name in self.get_tags():
            #print 'tag not in the note tags, return 0'
            return 0 #not related at all. May raise an error here TODO:
        
        relevant_tags = [tag_name]
        
        #merge code of direct parent with grand parents?TODO:
        direct_parent = tag_list[-2]
        relevant_tags.append(direct_parent)
        if direct_parent in self.get_tags():
            relevance += 10 * tag_list.index(direct_parent)
            
        
        ptf = Tag_Frame.objects.using(self.owner.username).get(name=direct_parent)
        ptf.owner_name = self.owner.username
        #print 'ptf.get_siblings(tag_name)', ptf.get_siblings(tag_name)
        for sib in ptf.get_siblings(tag_name):
            relevant_tags.append(sib)
            if sib in self.get_tags():
                relevance += 5
        
        #TODO: checking for cousins.
        #check for uncles
        grandparent_list = tag_list[:-2]
        grandparent_list.reverse()
        for i, grandparent in enumerate(grandparent_list):
            relevant_tags.append(grandparent)
            if grandparent in self.get_tags():
                relevance += 10 * tag_list.index(grandparent)
            child_tag_name = tag_list[-i-2]
            gtf = Tag_Frame.objects.using(self.owner.username).get(name=grandparent)
            #print 'child_tag_name:', child_tag_name, 'gtf', gtf
            gtf.owner_name = self.owner.username
            for sib in gtf.get_siblings(child_tag_name):
                relevant_tags.append(sib)
                if sib in self.get_tags():
                    relevance += len(tag_list) - i #check if always > 0
            
        #log.info('relevant_tags'+str(relevant_tags))
        for t in self.get_tags():
            if not t in relevant_tags:
                relevance -= 1
        
        return relevance    
       

class Social_Snippet(Social_Note):
    attachment = models.FileField(upload_to=get_storage_loc, max_length=100, blank=True, storage=fs, verbose_name=ugettext_lazy('Attachment'),)
    



class Social_Bookmark(Social_Note):
    url = models.CharField(max_length=2000)
    
    
    def __unicode__(self):
        return self.url + u' by ' + self.owner.username
    
    

class Social_Scrap(Social_Note):
    url = models.CharField(max_length=2000)
    
    
    def __unicode__(self):
        return self.url + u' by ' + self.owner.username



class Social_Frame(Social_Note):
    attachment = models.FileField(upload_to=get_storage_loc, max_length=100,  blank=True, storage=fs, verbose_name=ugettext_lazy('Attachment'),)   
    notes = models.ManyToManyField(Social_Note, related_name='in_frames', through="Social_Frame_Notes")
    
    def __unicode__(self):
        return ','.join([str(note.id) for note in self.notes.all()])   

    def get_notes_in_order(self, sort=None):        
        ns = [n for n in self.notes.all().order_by('in_frames')]
        #print 'ns:', ns
        if sort and sort == 'vote':
            ns.sort(key=lambda r: r.vote, reverse=True)  
        return ns
    
    
    def get_public_notes_in_order(self, sort=None):
        ns = [n for n in self.notes.all().order_by('in_frames') if n.private==False]
        if sort and sort == 'vote':
            ns.sort(key=lambda r: r.vote, reverse=True)  
        return ns
        
#===============================================================================
#    def display_notes(self):
#        return [[n.id, n.title, n.desc, n.vote, n.get_note_bookname(), n.get_note_type()] for n in self.notes.all().order_by('in_frames')] 
#                
#    
#    def display_public_notes(self):        
#        return [[n.id, n.title, n.desc, n.vote, n.get_note_bookname(), n.get_note_type()] for n in self.notes.all().order_by('in_frames') if n.private==False ] 
#===============================================================================

    def get_vote(self):        
        v = 0  
        for n in self.notes.all(): 
            v = v + n.vote
        return v


    def has_attachment(self):
        if hasattr(self, 'attachment') and self.attachment:
            return True
        notes = self.get_notes_in_order()        
        for note in notes:            
            if note.get_note_type() == 'Snippet' and note.social_snippet.has_attachment():                 
                return True
            if note.get_note_type() == 'Frame' and note.social_frame.has_attachment():                 
                return True
        return False



    def get_related_frames(self):        
        related = []    
        offsprings = self.get_offsprings()   
        for child in self.notes.filter(deleted=False):        
            
            uncles = child.get_frame_ids_titles()        
                  
            for uncle in uncles:        
                uncle.append('(note '+str(child.id)+')  '+child.title+':  '+child.desc)  
                if uncle[0] != self.id and uncle[0] not in self.get_offsprings() and uncle not in related:
                    #make it into a tuple so it can be hashed for soring later. (list cannot be hashed)
                    related.append((uncle[0],uncle[1],uncle[2]))        
            #for now, don't go up further TODO:
            if child.get_note_type() == 'Frame':            
                        
                related.extend(child.social_frame.get_related_frames())        
        #get a copy of related. Otherwise, removing item while iterating through the list will mess things up
        for nr in related[:]:            
            if nr[0] in self.get_offsprings():
                related.remove(nr)   
            if nr[0] == self.id:
                related.remove(nr)         
        related = list(set(related))        
        related.sort(key=lambda r: r[1],reverse = False) 
        return related   
 
 
    def get_size_of_related_frames(self):  
        return len(self.get_related_frames()) 
 
 
    def get_offsprings(self):
        offsprings = [n.id for n in self.notes.all()]
        for child in self.notes.all():            
            if child.get_note_type() == 'Frame':                  
                offsprings.extend(child.social_frame.get_offsprings())        
        return   offsprings        


    #TODO: check what social notes are private
    def get_public_offsprings(self):
        offsprings = [n.id for n in self.notes.filter(private=False)]
        for child in self.notes.all():            
            if child.get_note_type() == 'Frame':                  
                offsprings.extend(child.social_frame.get_offsprings())        
        return   offsprings



    def get_included_comments(self):
        ns = self.get_public_offsprings()
        comments = Social_Note_Comment.objects.filter(note__id__in=ns) 
        return comments
        
        

class Social_Frame_Notes(models.Model):
    social_frame = models.ForeignKey(Social_Frame, related_name='note_and_frame') #TODO:
    social_note = models.ForeignKey(Social_Note)
    
    class Meta:
        order_with_respect_to = 'social_frame'



class Social_Note_Taken(models.Model):
    note = models.ForeignKey(Social_Note)
    taker = models.ForeignKey(Member)
    init_date = models.DateTimeField('date created', auto_now_add=True)
    
    def __unicode__(self):
        #TODO:use ugettext for translation
        return self.taker.username+" taking "+self.note.owner.username+"'s note: "+self.note.desc
    

    class Meta:
        unique_together = (("note","taker"),)   
        
        

class Social_Note_Comment(models.Model):
    note =  models.ForeignKey(Social_Note)
    commenter = models.ForeignKey(Member)
    desc = models.TextField(max_length=2000)
    init_date = models.DateTimeField('date created', auto_now_add=True)
    
    def __unicode__(self):
        #TODO:use ugettext for translation
        return self.commenter.username+" on "+self.note.owner.username+"'s note: "+self.desc 

    class Meta:  
        unique_together = (("note","commenter", "desc"),)         
        ordering = ['-init_date','note','desc']




social_book_model_dict = {'notebook':Social_Note, 'snippetbook':Social_Snippet,'bookmarkbook':Social_Bookmark, 'scrapbook': Social_Scrap, 'framebook':Social_Frame}

def getSN(bookname):
    return social_book_model_dict.get(bookname)



class Social_Note_Course(models.Model):
    note =  models.ForeignKey(Social_Note)
    submitter = models.ForeignKey(Member)
    url = models.CharField(max_length=2000)
    init_date = models.DateTimeField('date created', auto_now_add=True)

    def __unicode__(self):        
        return self.url
    
    class Meta:
        ordering = ['-init_date','url']


#a simple implementation of backlinks. TODO:
#It tracks request's referrer.If it is from an external site, then put in this table.
class Social_Note_Backlink(models.Model):
    note =  models.ForeignKey(Social_Note)    
    url = models.CharField(max_length=2000)
    init_date = models.DateTimeField('date created', auto_now_add=True)

    def __unicode__(self):        
        return self.url
    
    class Meta:
        ordering = ['-init_date','url']
        
        

class Social_Note_Vote(models.Model):      
    note = models.ForeignKey(Social_Note)
    voter =  models.ForeignKey(Member)
    useful = models.BooleanField()#default??
    init_date = models.DateTimeField('date created', auto_now_add=True)

    class Meta:
        unique_together = (("note","voter"),)             
        ordering = ['-init_date','note'] 
    
    def __unicode__(self): 
        return self.note.__unicode__()+" voted by "+self.voter.__unicode__()



class Social_Area(models.Model):
    owner = models.ForeignKey(Member)
    owner_area_id = models.IntegerField(blank=True)
    name = models.CharField(max_length=150)
    #private = models.BooleanField(default=False)
    desc =  models.TextField(blank=True, max_length=2000)
    num_of_notes = models.IntegerField(default=0)
    area_tags = models.TextField(blank=True,max_length=2000, verbose_name=ugettext_lazy('Area Tags'))
    
    
    class Meta:
        ordering = ['name']
        unique_together = (('name','owner'),)



class Group(models.Model):
    name = models.CharField(blank=False,max_length=50, verbose_name=ugettext_lazy('Name'))
    desc = models.TextField(blank=True,max_length=500, verbose_name=ugettext_lazy('Description'))
    #these are the tags that really belong to the group, having these tags will surely be pushed to
    #this group 
    tags = models.ManyToManyField(Social_Tag)
    #other tags that can be related, but don't decide whether the notes belong to a group
    #extra_tags = models.ManyToManyField(Social_Tag)
    init_date = models.DateTimeField(verbose_name=ugettext_lazy('date created'), auto_now_add=True)
    private = models.BooleanField(blank=True,verbose_name=ugettext_lazy('Private'))     
    members = models.ManyToManyField(Member, related_name='members', verbose_name=ugettext_lazy('Members'))
    creator = models.ForeignKey(Member, verbose_name=ugettext_lazy('Creator'))#creater and admins have to be in members
    admins = models.ManyToManyField(Member, related_name='admins', verbose_name=ugettext_lazy('Admins')) #TODO: only one admin?
    icon = models.ImageField(upload_to=get_storage_loc,blank=True, storage=fs, verbose_name=ugettext_lazy('Icon')) 
    
    
    class Meta:
        #should name be unique?TODO:
        #unique_together = (("name"),)
        unique_together = (("name", 'creator'),)           
        ordering = ['name','-init_date']
    
    
    def __unicode__(self):
        return self.name
  
  
    #TODO: check amin right??
    def add_tags(self, username, tags_to_add):   
        pass
            
    
    #tags_to_add is a list of tag names
    def remove_tags(self, tags_to_remove):              
        pass
            
       
    def get_group_tag_name(self):
        return "sharinggroup:"+self.name        
        
     
    def get_tag_names(self):
        return [tag.name for tag in self.tags.all().order_by('name')]     

    def display_tags(self):      
        return ','.join(self.get_tag_names())
   

    def get_notes_today(self, bookname):
        note_list = self.get_notes(bookname)
        now = datetime.date.today()
        note_list = note_list.filter(init_date__day= now.day, init_date__month=now.month, init_date__year= now.year)        
        return note_list
                         
    
    def get_notes_this_week(self, bookname):
        note_list = self.get_notes(bookname)
        now = datetime.date.today()
        one_week_ago = now - datetime.timedelta(days=7)
        note_list = note_list.filter(init_date__gte=one_week_ago.strftime('%Y-%m-%d'),  init_date__lte=now.strftime('%Y-%m-%d 23:59:59'))        
        return note_list
      
    
    
    def get_notes(self, bookname):
        tag_names = [tag.name for tag in self.tags.all()]       
        q1 = Q(tags__name__in=tag_names, owner__in=self.members.all(), private=False)   
        q2 = Q(tags__name="sharinggroup:"+self.name, private=True) 
        note_list =  social_book_model_dict.get(bookname).objects.filter(q1 | q2).distinct() 
        return  note_list 
        
    
    
    def get_public_snippets_count(self):
        return self.get_notes('snippetbook').count()   
    
    def get_public_bookmarks_count(self):
        return self.get_notes('bookmarkbook').count()  
    
    def get_public_scraps_count(self):
        return self.get_notes('scrapbook').count()  
    
    def get_public_frames_count(self):
        return self.get_notes('framebook').count()  
    
    def get_public_notes_count(self):
        return self.get_notes('notebook').count()  
    
    
    #get tag frames made by the group members except the root one
    def get_tag_frames(self):
        tag_frames = []
        gtfs = Group_Tag_Frame.objects.filter(group=self) 
        print 'gtfs', gtfs
        for gtf in gtfs:  
            tag_frame = Tag_Frame.objects.using(gtf.tag_frame_owner.username).get(id=gtf.tag_frame_id) 
            tag_frames.append([tag_frame, gtf.tag_frame_owner] )
        return tag_frames
    
        
#Activity Stream such as adding friend, posting...
#class Activity(models.Model): 
#    pass





class Group_Tag_Frame(models.Model):
    group = models.ForeignKey(Group)
    #tag_frame_id in owner's db
    tag_frame_id = models.IntegerField()
    tag_frame_owner = models.ForeignKey(Member)






#one relation has one entry in this table (although two entries make it easy for query).  TODO: enforce no redundance?
#TODO: confirm          
class Friend_Rel(models.Model): 
    confirmed = models.BooleanField(default=False) 
    friend1 = models.ForeignKey(Member, related_name='friend1')
    friend2 = models.ForeignKey(Member, related_name='friend2')
    init_date = models.DateTimeField('date created', auto_now_add=True)

    def __unicode__(self): 
        return self.friend1.__unicode__()  + u" and " + self.friend2.__unicode__()
    
    def get_friend(self, member):
        if self.friend1 == member:
            return self.friend2
        if self.friend2 == member:
            return self.friend1
        else:
            return None
        
  
class Fan(models.Model):     
    idol = models.ForeignKey(Member, related_name='idol')
    fan = models.ForeignKey(Member, related_name='fan')
    #tags =
    init_date = models.DateTimeField('date created', auto_now_add=True)
    
    def __unicode__(self): 
        return self.fan.__unicode__()  + u" is a fan of " + self.idol.__unicode__()


    def get_feed_display(self):
        return u'<a href="/user/'+unicode(self.fan.id)+'/">'+ self.fan.__unicode__() + u'</a>' +\
               u'followed' + u'<a href="/user/' + unicode(self.idol.id) + u'/">' + self.idol.__unicode__()+ u'</a>'    



#Store the alternative language translation for notes.
class Social_Note_Translation(models.Model):
    note = models.ForeignKey(Social_Note)
    LANG_TYPE_CHOICES = (
        ('C', 'Chinese'),
        ('E', 'English'),
    )
    lang = models.CharField(max_length=1, choices=LANG_TYPE_CHOICES, verbose_name=ugettext_lazy('Language'),) #mark the language in the original note
    original_lang = models.CharField(max_length=1, choices=LANG_TYPE_CHOICES, verbose_name=ugettext_lazy('Original language'),)
    title = models.CharField(verbose_name=ugettext_lazy('Title'), blank=True,max_length=2000, help_text=_("The size of the title is limited to 2000 characaters."))
    desc =  models.TextField(verbose_name=ugettext_lazy('Description'), max_length=2000, blank=True,  help_text=_("The size of the desc is limited to 2000 characaters."))
    



#this can be used for individuals to invite users too.
class Invitation_Code(models.Model):
    code = models.CharField(verbose_name=ugettext_lazy('Invitation Code'), max_length=50)
    #For now, at most one group to add automatically for newly registered users.
    group = models.ForeignKey(Group, blank=True)
    max_size = models.IntegerField(default=100)
    current_size = models.IntegerField(default=0)
    expire_date = models.DateTimeField('Expiration date', auto_now_add=False)
    init_date = models.DateTimeField('date created', auto_now_add=True)
    
    def __unicode__(self):        
        return self.code+" for group "+self.group.name
    

    class Meta:
        unique_together = (("code"),)   
            
            
    def is_expired(self):
        if  self.expire_date < datetime.datetime.now():
            return True
        else:
            return False
    
    
       
        

class User_Reg_Invitation_Code(models.Model):  
   member =  models.ForeignKey(Member) 
   code =  models.ForeignKey(Invitation_Code) 
   init_date = models.DateTimeField('date created', auto_now_add=True)                                  