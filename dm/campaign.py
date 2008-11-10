# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
import datetime
import offer
import warnings
import netsvc
from mx import DateTime

from osv import fields
from osv import osv


class dm_campaign_group(osv.osv):
    _name = "dm.campaign.group"

    def _quantity_estimated_total(self, cr, uid, ids, name, args, context={}):
        result={}
        numeric=True
        quantity=0
        groups = self.browse(cr,uid,ids)
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                if campaign.quantity_estimated_total.isdigit():
                    quantity += int(campaign.quantity_estimated_total)
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        print "Estimated : ",result
        return result

    def _quantity_wanted_total(self, cr, uid, ids, name, args, context={}):
        result={}
        numeric=True
        quantity=0
        groups = self.browse(cr,uid,ids)
        print "ids : ",ids
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                print "wanted total : ", campaign.quantity_wanted_total
                if campaign.quantity_wanted_total.isdigit():
                    quantity += int(campaign.quantity_wanted_total)
                elif campaign.quantity_wanted_total == "AAA for a Segment":
                    result[group.id]='AAA for a Segment'
                    numeric=False
                    break
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        print "Wanted : ",result
        return result

    def _quantity_delivered_total(self, cr, uid, ids, name, args, context={}):
        result={}
        numeric=True
        quantity=0
        groups = self.browse(cr,uid,ids)
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                if campaign.quantity_delivered_total.isdigit():
                    quantity += int(campaign.quantity_delivered_total)
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        print "Delivered : ",result
        return result

    def _quantity_usable_total(self, cr, uid, ids, name, args, context={}):
        result={}
        quantity=0
        numeric=True
        groups = self.browse(cr,uid,ids)
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                if campaign.quantity_usable_total.isdigit():
                    quantity += int(campaign.quantity_usable_total)
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        print "Usable : ",result
        return result

    def _camp_group_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        offer_code = ''
        offer_name = ''
        for id in ids:

            dt = time.strftime('%Y-%m-%d')
            date = dt.split('-')
            year = month = ''
            if len(date)==3:
                year = date[0][2:]
                month = date[1]
            final_date=year+month
            grp = self.browse(cr,uid,id)
            for c in grp.campaign_ids:
                if c.offer_id:
                    d = self.pool.get('dm.offer').browse(cr, uid, c.offer_id.id)
                    offer_code = d.code
                    offer_name = d.name
            code1='-'.join([final_date,offer_code, offer_name])
            result[id]=code1
        return result

    _columns = {
        'name': fields.char('Campaign group name', size=64, required=True),
        'code' : fields.function(_camp_group_code,string='Code',type='char',method=True,readonly=True),
        'project_id' : fields.many2one('project.project', 'Project', readonly=True),
        'campaign_ids': fields.one2many('dm.campaign', 'campaign_group_id', 'Campaigns', domain=[('campaign_group_id','=',False)], readonly=True),
        'purchase_line_ids': fields.one2many('dm.campaign.purchase_line', 'campaign_group_id', 'Purchase Lines'),
        'quantity_estimated_total' : fields.function(_quantity_estimated_total, string='Total Estimated Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_wanted_total' : fields.function(_quantity_wanted_total, string='Total Wanted Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_delivered_total' : fields.function(_quantity_delivered_total, string='Total Delivered Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_usable_total' : fields.function(_quantity_usable_total, string='Total Usable Quantity',type="char",size="64",method=True,readonly=True),
    }
dm_campaign_group()


class dm_campaign_type(osv.osv):
    _name = "dm.campaign.type"

    _columns = {
        'name': fields.char('Description', size=64, translate=True, required=True),
        'code': fields.char('Code', size=16, translate=True, required=True),
        'description': fields.text('Description', translate=True),
    }
dm_campaign_type()


class dm_overlay(osv.osv):
    _name = 'dm.overlay'
    _rec_name = 'trademark_id'

    def create(self,cr,uid,vals,context={}):
        id = super(dm_overlay,self).create(cr,uid,vals,context)
        data = self.browse(cr, uid, id)
        overlay_country_ids = [country_ids.id for country_ids in data.country_ids]
        dealer_country_ids = [country_ids.id for country_ids in data.dealer_id.country_ids]
        for i in overlay_country_ids:
            if not i in dealer_country_ids:
                raise  osv.except_osv('Warning', "This country is not allowed for %s" % (data.dealer_id.name,) )
        return id

    def _overlay_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:

            overlay = self.browse(cr,uid,id)
            trademark_code = overlay.trademark_id.code or ''
            dealer_code = overlay.dealer_id.ref or ''
            code1='-'.join([trademark_code, dealer_code])
            result[id]=code1
        return result

    _columns = {
        'code' : fields.function(_overlay_code,string='Code',type='char',method=True,readonly=True),
        'trademark_id' : fields.many2one('dm.trademark', 'Trademark', required=True),
        'dealer_id' : fields.many2one('res.partner', 'Dealer',domain=[('category_id','ilike','Dealer')], context={'category':'Dealer'}, required=True),
        'country_ids' : fields.many2many('res.country', 'overlay_country_rel', 'overlay_id', 'country_id', 'Country', required=True),
        'bank_account_id' : fields.many2one('account.account', 'Account'),
    }
dm_overlay()


class one2many_mod_task(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not context:
            context = {}
        if not values:
                values = {}
        res = {}
        for id in ids:
            res[id] = []
        for id in ids:
            query = "select project_id from dm_campaign where id = %i" %id
            cr.execute(query)
            project_ids = [ x[0] for x in cr.fetchall()]
            if name[0] == 'd':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','DTP')], limit=self._limit)
            elif name[0] == 'm':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Mailing Manufacturing')], limit=self._limit)
            elif name[0] == 'c':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Customers List')], limit=self._limit)
            else :
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Mailing Manufacturing')], limit=self._limit)
            for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
                res[id].append( r['id'] )
        return res

class dm_campaign(osv.osv):
    _name = "dm.campaign"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _rec_name = 'name'

    def dtp_making_time_get(self, cr, uid, ids, name, arg, context={}):
        result={}
        for i in ids:
            result[i]=0.0
        return result

    def _campaign_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            camp = self.browse(cr,uid,[id])[0]
            offer_code = camp.offer_id and camp.offer_id.code or ''
            trademark_code = camp.trademark_id and camp.trademark_id.code or ''
            dealer_code =camp.dealer_id and camp.dealer_id.ref or ''
            date_start = camp.date_start or ''
            country_code = camp.country_id.code or ''
            date = date_start.split('-')
            year = month = ''
            if len(date)==3:
                year = date[0][2:]
                month = date[1]
            final_date=month+year
            code1='-'.join([offer_code ,dealer_code ,trademark_code ,final_date ,country_code])
            result[id]=code1
        return result

    def _get_campaign_type(self,cr,uid,context={}):
        campaign_type = self.pool.get('dm.campaign.type')
        type_ids = campaign_type.search(cr,uid,[])
        type = campaign_type.browse(cr,uid,type_ids)
        return map(lambda x : [x.code,x.name],type)

    def onchange_lang_currency(self, cr, uid, ids, country_id):
        value = {}
        if country_id:
            country = self.pool.get('res.country').browse(cr,uid,[country_id])[0]
            value['lang_id'] =  country.main_language.id
            value['currency_id'] = country.main_currency.id
        else:
            value['lang_id']=0
            value['currency_id']=0
        return {'value':value}

    def _quantity_estimated_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_estimated.isdigit():
                    quantity += int(propo.quantity_estimated)
                else:
                    result[campaign.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[campaign.id]=str(quantity)
        return result

    def _quantity_wanted_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_wanted.isdigit():
                    quantity += int(propo.quantity_wanted)
                elif propo.quantity_wanted == "AAA for a Segment":
                    result[campaign.id]='AAA for a Segment'
                    numeric=False
                    break
                else:
                    result[campaign.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[campaign.id]=str(quantity)
        return result

    def _quantity_delivered_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_delivered.isdigit():
                    quantity += int(propo.quantity_delivered)
                else:
                    result[campaign.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[campaign.id]=str(quantity)
        return result

    def _quantity_usable_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_usable.isdigit():
                    quantity += int(propo.quantity_usable)
                else:
                    result[campaign.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[campaign.id]=str(quantity)
        return result


    _columns = {
        'code1' : fields.function(_campaign_code,string='Code',type="char",size="64",method=True,readonly=True),
        'offer_id' : fields.many2one('dm.offer', 'Offer',domain=[('state','=','open'),('type','in',['new','standart','rewrite'])], required=True,
            help="Choose the commercial offer to use with this campaign, only offers in open state can be assigned"),
        'country_id' : fields.many2one('res.country', 'Country',required=True, 
            help="The language and currency will be automaticaly assigned if they are defined for the country"),
        'lang_id' : fields.many2one('res.lang', 'Language'),
        'trademark_id' : fields.many2one('dm.trademark', 'Trademark'),
        'project_id' : fields.many2one('project.project', 'Project', readonly=True,
            help="Generating the Retro Planning will create and assign the different tasks used to plan and manage the campaign"),
        'campaign_group_id' : fields.many2one('dm.campaign.group', 'Campaign group'),
        'notes' : fields.text('Notes'),
        'proposition_ids' : fields.one2many('dm.campaign.proposition', 'camp_id', 'Proposition'),
        'campaign_type' : fields.selection(_get_campaign_type,'Type'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'planning_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Planning Status',readonly=True),
        'items_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Items Status',readonly=True),
        'translation_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Translation Status',readonly=True),
        'manufacturing_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Manufacturing Status',readonly=True),
        'customer_file_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Customers Files Status',readonly=True),
        'dealer_id' : fields.many2one('res.partner', 'Dealer',domain=[('category_id','ilike','Dealer')], context={'category':'Dealer'},
            help="The dealer is the partner the campaign is planned for"),
        'responsible_id' : fields.many2one('res.users','Responsible'),
        'manufacturing_responsible_id' : fields.many2one('res.users','Responsible'),
        'dtp_responsible_id' : fields.many2one('res.users','Responsible'),
        'files_responsible_id' : fields.many2one('res.users','Responsible'),
        'invoiced_partner_id' : fields.many2one('res.partner','Invoiced Partner'),
        'files_delivery_address_id' : fields.many2one('res.partner.address','Delivery Address'),
        'dtp_making_time' : fields.function(dtp_making_time_get, method=True, type='float', string='Making Time'),
        'deduplicator_id' : fields.many2one('res.partner','Deduplicator',domain=[('category_id','ilike','Deduplicator')], context={'category':'Deduplicator'},
            help="The deduplicator is a partner responsible to remove identical addresses from the customers list"),
        'cleaner_id' : fields.many2one('res.partner','Cleaner',domain=[('category_id','ilike','Cleaner')], context={'category':'Cleaner'},
            help="The cleaner is a partner responsible to remove bad addresses from the customers list"),
        'currency_id' : fields.many2one('res.currency','Currency',ondelete='cascade'),
        'manufacturing_cost_ids': fields.one2many('dm.campaign.manufacturing_cost','campaign_id','Manufacturing Costs'),
        'manufacturing_product': fields.many2one('product.product','Manufacturing Product'),
        'purchase_line_ids': fields.one2many('dm.campaign.purchase_line', 'campaign_id', 'Purchase Lines'),
        'overlay_id': fields.many2one('dm.overlay', 'Overlay'),
        'owner_id' : fields.many2one('res.partner', 'Owner',domain=[('category_id','ilike','Owner')], context={'category':'Owner'}),
        'router_id' : fields.many2one('res.partner', 'Router',domain=[('category_id','ilike','Router')], context={'category':'Router'}),
        'dtp_task_ids': one2many_mod_task('project.task', 'project_id', "DTP tasks",
                                                        domain=[('type','ilike','DTP')], context={'type':'DTP'}),
        'manufacturing_task_ids': one2many_mod_task('project.task', 'project_id', "Manufacturing tasks",
                                                        domain=[('type','ilike','Mailing Manufacturing')],context={'type':'Mailing Manufacturing'}),
        'cust_file_task_ids': one2many_mod_task('project.task', 'project_id', "Customer Files tasks",
                                                        domain=[('type','ilike','Customers List')], context={'type':'Customers List'}),
        'quantity_estimated_total' : fields.function(_quantity_estimated_total, string='Total Estimated Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_wanted_total' : fields.function(_quantity_wanted_total, string='Total Wanted Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_delivered_total' : fields.function(_quantity_delivered_total, string='Total Delivered Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_usable_total' : fields.function(_quantity_usable_total, string='Total Usable Quantity',type="char",size="64",method=True,readonly=True),
    }

    _defaults = {
        'state': lambda *a: 'draft',
        'manufacturing_state': lambda *a: 'pending',
        'items_state': lambda *a: 'pending',
        'translation_state': lambda *a: 'pending',
        'customer_file_state': lambda *a: 'pending',
        'campaign_type': lambda *a: 'general',
        'responsible_id' : lambda obj, cr, uid, context: uid,
    }

    def state_draft_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def state_close_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'close'})
        return True

    def state_pending_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'pending'})
        return True

    def state_open_set(self, cr, uid, ids, *args):
        camp = self.browse(cr,uid,ids)[0]
        if camp.offer_id:
            forbidden_state_ids = [state_id.country_id.id for state_id in camp.offer_id.forbidden_state_ids]
            forbidden_country_ids = [country_id.id for country_id in camp.offer_id.forbidden_country_ids]
            forbidden_country_ids.extend(forbidden_state_ids)
            if camp.offer_id.forbidden_country_ids and camp.country_id.id  in  forbidden_country_ids :
                raise osv.except_osv("Error!!","This offer is not valid in this country")
        if not camp.date_start or not camp.dealer_id or not camp.trademark_id :
            raise osv.except_osv("Error!!","Informations are missing. Check Date Start, Dealer and Trademark")
        super(dm_campaign,self).write(cr, uid, ids, {'state':'open','planning_state':'inprogress'})
        return True

    def write(self, cr, uid, ids, vals, context=None):
        res = super(dm_campaign,self).write(cr, uid, ids, vals, context)
        camp = self.pool.get('dm.campaign').browse(cr,uid,ids)[0]
        srch_offer_ids = self.search(cr, uid, [('offer_id', '=', camp.offer_id.id)])

        c = camp.country_id.id
        if 'date_start' in vals and vals['date_start']:
            time_format = "%Y-%m-%d"
            d = time.strptime(vals['date_start'],time_format)
            d = datetime.date(d[0], d[1], d[2])
            date_end = d + datetime.timedelta(days=365)
            super(osv.osv,self).write(cr, uid, camp.id, {'date':date_end})
            if camp.project_id:
                self.pool.get('project.project').write(cr,uid,[camp.project_id.id],{'date_end':vals['date_start']})
        if camp.offer_id:
            d = camp.offer_id.id
            offers = self.pool.get('dm.offer').browse(cr, uid, d)
            list_off = []
            for off in offers.forbidden_country_ids:
                list_off.append(off.id)
                if c in list_off:
                    raise osv.except_osv("Error!!","You cannot use this offer in this country")

            """ In campaign, if no trademark is given, it gets the 'recommended trademark' from offer """
            if not camp.trademark_id:
                super(osv.osv, self).write(cr, uid, camp.id, {'trademark_id':offers.recommended_trademark.id})

        # check if an overlay exists else create it
        overlay_country_ids=[]
        camp1 = self.browse(cr, uid, camp.id)
        if camp1.trademark_id and camp1.dealer_id and camp1.country_id:
            overlay = self.pool.get('dm.overlay').search(cr, uid, [('trademark_id','=',camp1.trademark_id.id), ('dealer_id','=',camp1.dealer_id.id)])

            for o_id in overlay:
                browse_overlay = self.pool.get('dm.overlay').browse(cr, uid, o_id)
                overlay_country_ids = [country_ids.id for country_ids in browse_overlay.country_ids]

            if overlay and (camp1.country_id.id in overlay_country_ids):
                super(osv.osv, self).write(cr, uid, camp1.id, {'overlay_id':overlay[0]}, context)  
            elif overlay and not (camp1.country_id.id in overlay_country_ids):
                overlay_country_ids.append(camp1.country_id.id)
                self.pool.get('dm.overlay').write(cr, uid, browse_overlay.id, {'country_ids':[[6,0,overlay_country_ids]]}, context)
                super(osv.osv, self).write(cr, uid, camp1.id, {'overlay_id':overlay[0]}, context)
            else:
                overlay_country_ids.append(camp1.country_id.id)
                overlay_ids1 = self.pool.get('dm.overlay').create(cr, uid, {'trademark_id':camp1.trademark_id.id, 'dealer_id':camp1.dealer_id.id, 'country_ids':[[6,0,overlay_country_ids]]}, context)
                super(osv.osv, self).write(cr, uid, camp1.id, {'overlay_id':overlay_ids1}, context)
        else:
            super(osv.osv, self).write(cr, uid, camp1.id, {'overlay_id':0}, context)

        return res

    def create(self,cr,uid,vals,context={}):
        if context.has_key('campaign_type') and context['campaign_type']=='model':
            vals['campaign_type']='model'

        id_camp = super(dm_campaign,self).create(cr,uid,vals,context)

        data_cam = self.browse(cr, uid, id_camp)
        # Set campaign end date at one year after start date
        if (data_cam.date_start) and (not data_cam.date):
            time_format = "%Y-%m-%d"
            d = time.strptime(data_cam.date_start,time_format)
            d = datetime.date(d[0], d[1], d[2])
            date_end = d + datetime.timedelta(days=365)
            super(dm_campaign,self).write(cr, uid, id_camp, {'date':date_end})

        # Set trademark to offer's trademark only if trademark is null
        if not vals['campaign_type'] == 'model':
            if vals['offer_id'] and (not vals['trademark_id']):
                offer_id = self.pool.get('dm.offer').browse(cr, uid, vals['offer_id'])
                super(dm_campaign,self).write(cr, uid, id_camp, {'trademark_id':offer_id.recommended_trademark.id})

        # check if an overlay exists else create it
        data_cam1 = self.browse(cr, uid, id_camp)
        overlay_country_ids = []
        if data_cam1.trademark_id and data_cam1.dealer_id and data_cam1.country_id:
            overlay = self.pool.get('dm.overlay').search(cr, uid, [('trademark_id','=',data_cam1.trademark_id.id), ('dealer_id','=',data_cam1.dealer_id.id)])
            for o_id in overlay:
                browse_overlay = self.pool.get('dm.overlay').browse(cr, uid, o_id)
                overlay_country_ids = [country_ids.id for country_ids in browse_overlay.country_ids]
            if overlay and (data_cam1.country_id.id in overlay_country_ids):
                super(osv.osv, self).write(cr, uid, data_cam1.id, {'overlay_id':overlay[0]}, context)  
            elif overlay and not (data_cam1.country_id.id in overlay_country_ids):
                overlay_country_ids.append(data_cam1.country_id.id)
                self.pool.get('dm.overlay').write(cr, uid, browse_overlay.id, {'country_ids':[[6,0,overlay_country_ids]]}, context)
                super(osv.osv, self).write(cr, uid, data_cam1.id, {'overlay_id':overlay[0]}, context)
            else:
                overlay_country_ids.append(data_cam1.country_id.id)
                overlay_ids1 = self.pool.get('dm.overlay').create(cr, uid, {'trademark_id':data_cam1.trademark_id.id, 'dealer_id':data_cam1.dealer_id.id, 'country_ids':[[6,0,overlay_country_ids]]}, context)
                super(osv.osv, self).write(cr, uid, data_cam1.id, {'overlay_id':overlay_ids1}, context)

        return id_camp

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        result = super(dm_campaign,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
        if context.has_key('campaign_type'):
            if context['campaign_type'] == 'model' :
                if result.has_key('toolbar'):
                    result['toolbar']['action'] =[]
        return result

    def copy_campaign(self,cr, uid, ids, *args):
        camp = self.browse(cr,uid,ids)[0]
        default={}
        default['name']='New campaign from model %s' % camp.name
        default['campaign_type'] = 'recruiting'
        default['responsible_id'] = uid
        self.copy(cr,uid,ids[0],default)
        return True
    
    def copy(self, cr, uid, id, default=None, context={}):
        cmp_id = super(dm_campaign, self).copy(cr, uid, id, default, context=context)
        data = self.browse(cr, uid, cmp_id, context)
        name_default='Copy of %s' % data.name
        super(dm_campaign, self).write(cr, uid, cmp_id, {'name':name_default, 'date_start':0, 'date':0, 'project_id':0})
        return cmp_id
    
dm_campaign()


class dm_campaign_proposition(osv.osv):
    _name = "dm.campaign.proposition"
    _inherits = {'account.analytic.account': 'analytic_account_id'}

    def write(self, cr, uid, ids, vals, context=None):
        res = super(dm_campaign_proposition,self).write(cr, uid, ids, vals, context)
        camp = self.pool.get('dm.campaign.proposition').browse(cr,uid,ids)[0]
        c = camp.camp_id.id
        id = self.pool.get('dm.campaign').browse(cr, uid, c)
        if not camp.date_start:
            super(osv.osv, self).write(cr, uid, camp.id, {'date_start':id.date_start})
        return res

    def create(self,cr,uid,vals,context={}):
        id = self.pool.get('dm.campaign').browse(cr, uid, vals['camp_id'])
        if not vals['date_start']:
            if id.date_start:
                vals['date_start']=id.date_start
        return super(dm_campaign_proposition, self).create(cr, uid, vals, context)

    def copy(self, cr, uid, id, default=None, context={}):
        """
        Function to duplicate segments only if 'keep_segments' is set to yes else not to duplicate segments
        """
        proposition_id = super(dm_campaign_proposition, self).copy(cr, uid, id, default, context=context)
        data = self.browse(cr, uid, proposition_id, context)
        default='Copy of %s' % data.name
        super(dm_campaign_proposition, self).write(cr, uid, proposition_id, {'name':default, 'date_start':0, 'initial_proposition_id':id})
        if data.keep_segments == False:
            l = []
            for i in data.segment_ids:
                 l.append(i.id)
                 self.pool.get('dm.campaign.proposition.segment').unlink(cr,uid,l)
                 super(dm_campaign_proposition, self).write(cr, uid, proposition_id, {'segment_ids':[(6,0,[])]})
            return proposition_id
        """
        Function to duplicate segments only if 'keep_prices' is set to yes else not to duplicate products
        """
        if data.keep_prices == False:
            l = []
            for i in data.product_ids:
                 l.append(i.id)
                 self.pool.get('dm.product').unlink(cr,uid,l)
                 super(dm_campaign_proposition, self).write(cr, uid, proposition_id, {'product_ids':[(6,0,[])]})
            return proposition_id
        return proposition_id

    def _proposition_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            pro = self.browse(cr,uid,[id])[0]
            camp_code = pro.camp_id.code1 or ''
            offer_code = pro.camp_id.offer_id and pro.camp_id.offer_id.code or ''
            trademark_code = pro.camp_id.trademark_id and pro.camp_id.trademark_id.name or ''
            dealer_code =pro.camp_id.dealer_id and pro.camp_id.dealer_id.ref or ''
            date_start = pro.date_start or ''
            date = date_start.split('-')
            year = month = ''
            if len(date)==3:
                year = date[0][2:]
                month = date[1]
            country_code = pro.camp_id.country_id.code or ''
            seq = '%%0%sd' % 2 % id
            final_date = month+year
            code1='-'.join([camp_code, seq])
            result[id]=code1
        return result

    def _quantity_wanted_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            numeric=True
            for segment in propo.segment_ids:
                if segment.all_add_avail:
                    result[propo.id]='AAA for a Segment'
                    numeric=False
                    continue
                if not segment.quantity_wanted:
                    result[propo.id]='Wanted Quantity missing in a Segment'
                    numeric=False
                    continue
                qty += segment.quantity_wanted
            if numeric:
                result[propo.id]=str(qty)
        return result

    def _quantity_estimated_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_estimated == 0:
                    result[propo.id]='Estimated Quantity missing in a Segment'
                    continue
                qty += segment.quantity_estimated
            result[propo.id]=str(qty)
        return result

    def _quantity_delivered_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_delivered == 0:
                    result[propo.id]='Delivered Quantity missing in a Segment'
                    continue
                qty += segment.quantity_delivered
            result[propo.id]=str(qty)
        return result

    def _quantity_usable_get(self, cr, uid, ids, name, args, context={}):
        result={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_usable == 0:
                    result[propo.id]='Usable Quantity missing in a Segment'
                    continue
                qty += segment.quantity_usable
            result[propo.id]=str(qty)
        return result


    def _default_camp_date(self, cr, uid, context={}):
        if 'date1' in context and context['date1']:
            dd = context['date1']
            return dd
        return []

    _columns = {
        'code1' : fields.function(_proposition_code,string='Code',type="char",size="64",method=True,readonly=True),
        'camp_id' : fields.many2one('dm.campaign','Campaign',ondelete = 'cascade',required=True),
        'delay_ids' : fields.one2many('dm.campaign.delay', 'proposition_id', 'Delays', ondelete='cascade'),
        'sale_rate' : fields.float('Sale Rate (%)', digits=(16,2),
                    help='This is the estimated sale rate (in percent) for this commercial proposition'),
        'proposition_type' : fields.selection([('init','Initial'),('relaunching','Relauching'),('split','Split')],"Type"),
        'initial_proposition_id': fields.many2one('dm.campaign.proposition', 'Initial proposition', readonly=True),
        'segment_ids' : fields.one2many('dm.campaign.proposition.segment','proposition_id','Segment', ondelete='cascade'),
        'quantity_estimated' : fields.function(_quantity_estimated_get,string='Estimated Quantity',type="char",size="64",method=True,readonly=True,
                    help='The Estimated quantity is an estimation of the usable quantity of addresses you  will get after delivery, deduplication and cleaning\n' \
                            'This is usually the quantity used to order the manufacturing of the mailings'),
        'quantity_wanted' : fields.function(_quantity_wanted_get,string='Wanted Quantity',type="char",size="64",method=True,readonly=True,
                    help='The wanted quantity is the number of addresses you wish to get for that segment.\n' \
                            'This is usually the quantity used to order Customers Lists\n' \
                            'The wanted quantity could be AAA for All Addresses Available'),
        'quantity_delivered' : fields.function(_quantity_delivered_get,string='Delivered Quantity',type="char",size="64",method=True,readonly=True,
                    help='The delivered quantity is the number of addresses you receive from the broker.'),
        'quantity_usable' : fields.function(_quantity_usable_get,string='Usable Quantity',type="char",size="64",method=True,readonly=True,
                    help='The usable quantity is the number of addresses you have after delivery, deduplication and cleaning.'),
        'quantity_real': fields.integer('Real Quantity'),
        'starting_mail_price' : fields.float('Starting Mail Price',digits=(16,2)),
        'customer_pricelist_id':fields.many2one('product.pricelist','Items Pricelist', required=False),
        'forwarding_charges' : fields.float('Forwarding Charges', digits=(16,2)),
        'notes':fields.text('Notes'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'product_ids' : fields.one2many('dm.product', 'proposition_id', 'Catalogue'),
#        'product_ids' : fields.many2many('dm.product', 'proposition_product_rel', 'proposition_id', 'product_id', 'Catalogue'),
        'payment_methods' : fields.many2many('account.journal','campaign_payment_method_rel','proposition_id','journal_id','Payment Methods',domain=[('type','=','cash')]),
        'keep_segments' : fields.boolean('Keep Segments'),
        'keep_prices' : fields.boolean('Keep Prices At Duplication'),
        'force_sm_price' : fields.boolean('Force Starting Mail Price'),
        'sm_price' : fields.float('Starting Mail Price', digits=(16,2)),
#        'prices_prog_id' : fields.many2one('dm.campaign.proposition.prices_progression', 'Prices Progression'),
        'manufacturing_costs': fields.float('Manufacturing Costs',digits=(16,2)),
    }

    _defaults = {
        'proposition_type' : lambda *a : 'init',
        'date_start' : _default_camp_date,
        'keep_segments' : lambda *a : True,
        'keep_prices' : lambda *a : True
    }

    def _check(self, cr, uid, ids=False, context={}):
        '''
        Function called by the scheduler to create workitem from the segments of propositions.
        '''
        ids = self.search(cr,uid,[('date_start','=',time.strftime('%Y-%m-%d %H:%M:%S'))])
        for id in ids:
            res = self.browse(cr,uid,[id])[0]
            offer_step_id = self.pool.get('dm.offer.step').search(cr,uid,[('offer_id','=',res.camp_id.offer_id.id),('flow_start','=',True)])
            if offer_step_id :
                for segment in res.segment_ids:
                    vals = {'step_id':offer_step_id[0],'segment_id':segment.id}
                    new_id = self.pool.get('dm.offer.step.workitem').create(cr,uid,vals)
        return True

dm_campaign_proposition()

class dm_campaign_proposition_segment(osv.osv):

    _name = "dm.campaign.proposition.segment"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _description = "Segment"

    def _quantity_usable_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for segment in self.browse(cr,uid,ids):
            result[segment.id]=segment.quantity_delivered - segment.quantity_dedup_dedup - segment.quantity_cleaned_dedup - segment.quantity_dedup_cleaner- segment.quantity_cleaned_cleaner
        return result

    def write(self, cr, uid, ids, vals, context=None):
        list_name = self.pool.get('dm.customers_list').browse(cr, uid, vals['list_id'])
        segs = self.browse(cr, uid, ids)[0]
        if 'start_census' in vals and vals['start_census']:
            start_census = vals['start_census']
        else:
            start_census = segs.start_census
        if 'end_census' in vals and vals['end_census']:
            end_census = vals['end_census']
        else:
            end_census = segs.end_census
        vals['name'] = list_name.name + '-' + str(start_census) + '/' + str(end_census)
        return super(dm_campaign_proposition_segment,self).write(cr, uid, ids, vals, context)

    def create(self,cr,uid,vals,context={}):
        list_name = self.pool.get('dm.customers_list').browse(cr, uid, vals['list_id'])
        vals['name'] = list_name.name + '-' + str(vals['start_census']) + '/' + str(vals['end_census'])
        return super(dm_campaign_proposition_segment, self).create(cr, uid, vals, context)

    def _segment_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            seg = self.browse(cr,uid,[id])[0]
            country_code = seg.proposition_id.camp_id.country_id.code or ''
            if seg.list_id:
                cust_file_code =  seg.list_id.code
                seq = '%%0%sd' % 2 % id
                code1='-'.join([country_code[:3], cust_file_code[:3], seq[:4]])
            else:
                code1='No File Defined'
            result[id]=code1
        return result

    _columns = {
        'code1' : fields.function(_segment_code,string='Code',type="char",size="64",method=True,readonly=True),
        'proposition_id' : fields.many2one('dm.campaign.proposition','Proposition', ondelete='cascade'),
        'list_id': fields.many2one('dm.customers_list','Customers List',required=True),
        'quantity_estimated' : fields.integer('Estimated Quantity'),
        'quantity_wanted' : fields.integer('Wanted Quantity'),
        'quantity_delivered' : fields.integer('Delivered Quantity'),
        'quantity_dedup_dedup' : fields.integer('Deduplication Quantity'),
        'quantity_dedup_cleaner' : fields.integer('Deduplication Quantity'),
        'quantity_cleaned_dedup' : fields.integer('Cleaned Quantity'),
        'quantity_cleaned_cleaner' : fields.integer('Cleaned Quantity'),
        'quantity_usable' : fields.function(_quantity_usable_get,string='Usable Quantity',type="integer",method=True,readonly=True),
        'AAA': fields.boolean('All Adresses Available'),
        'all_add_avail': fields.boolean('All Adresses Available'),
        'split_id' : fields.many2one('dm.campaign.proposition.segment','Split'),
        'start_census' :fields.integer('Start Census (days)'),
        'end_census' : fields.integer('End Census (days)'),
        'deduplication_level' : fields.integer('Deduplication Level'),
        'active' : fields.boolean('Active'),
        'reuse_id' : fields.many2one('dm.campaign.proposition.segment','Reuse'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'note' : fields.text('Notes'),
        'segmentation_criteria': fields.text('Segmentation Criteria'),
        'price_per_thousand' : fields.integer('Price per 1000'),
    }
    _order = 'deduplication_level'

dm_campaign_proposition_segment()

class dm_campaign_delay(osv.osv):
    _name = "dm.campaign.delay"
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'value' : fields.integer('Value'),
        'proposition_id' : fields.many2one('dm.campaign.proposition', 'Proposition')
    }

dm_campaign_delay()


PURCHASE_LINE_TRIGGERS = [
    ('draft','At Draft'),
    ('open','At Open'),
    ('planned','At Planning'),
    ('close','At Close'),
    ('manual','Manual'),
]

PURCHASE_LINE_STATES = [
    ('pending','Pending'),
    ('requested','Quotations Requested'),
    ('ordered','Ordered'),
    ('delivered','Delivered'),
]

PURCHASE_LINE_TYPES = [
    ('manufacturing','Manufacturing'),
    ('items','Items'),
    ('customer_file','Customer Files'),
    ('translation','Translation'),
    ('dtp','DTP'),
]

QTY_TYPES = [
    ('quantity_estimated','Estimated Quantity'),
    ('quantity_wanted','Wanted Quantity'),
    ('quantity_delivered','Delivered Quantity'),
    ('quantity_usable','Usable Quantity'),
    ('quantity_free','Free Quantity'),
]

DOC_TYPES = [
    ('po','Purchase Order'),
    ('rfq','Request For Quotation'),
]

class dm_campaign_purchase_line(osv.osv):
    _name = 'dm.campaign.purchase_line'
    _rec_name = 'product_id'

    def _get_uom_id(self, cr, uid, *args):
        cr.execute('select id from product_uom order by id limit 1')
        res = cr.fetchone()
        return res and res[0] or False

    def quantity_get(self,cr, uid, ids, *args):
        value = {}
        quantity = 0

        pline = self.browse(cr, uid, ids)[0]
#        if not pline.campaign_id:
#            raise  osv.except_osv('Warning', "You must first save this Purchase Line and the campaign before using this button")

        if pline.campaign_group_id:
            obj = pline.campaign_group_id
        else:
            obj = pline.campaign_id

        if pline.type_quantity == 'quantity_free':
            if not quantity:
                quantity = 0
        elif pline.type_quantity == 'quantity_estimated':
            if obj.quantity_estimated_total.isdigit():
                quantity = obj.quantity_estimated_total
            else :
                raise osv.except_osv('Warning',
                    'Cannot get wanted quantity, check prososition segments')
        elif pline.type_quantity == 'quantity_wanted':
            if obj.quantity_wanted_total.isdigit():
                quantity = obj.quantity_wanted_total
            elif obj.quantity_wanted_total == 'AAA for a Segment':
                quantity = 0
            else :
                raise osv.except_osv('Warning',
                    "Cannot get wanted quantity, check prososition segments")
        elif pline.type_quantity == 'quantity_delivered':
            if obj.quantity_delivered_total.isdigit():
                quantity = obj.quantity_delivered_total
            else :
                raise osv.except_osv('Warning',
                    "Cannot get delivered quantity, check prososition segments")
        elif pline.type_quantity == 'quantity_usable':
            if obj.quantity_usable_total.isdigit():
                quantity = obj.quantity_usable_total
            else :
                raise osv.except_osv('Warning',
                    "Cannot get usable quantity, check prososition segments")
        else:
            raise osv.except_osv('Warning','Error getting quantity')

        pline.write({'quantity':quantity})

        return True


    def po_generate(self,cr, uid, ids, *args):
        plines = self.browse(cr, uid ,ids)

        if not plines:
            raise  osv.except_osv('Warning', "There's no purchase lines defined")

        for pline in plines:
            if pline.state == 'pending':

                print "Campaign ID : ",pline.campaign_id
                print "Group ID : ",pline.campaign_group_id

                # if in a group, obj = 1st campaign of the group, if not it's the campaing
                if pline.campaign_group_id:
                    obj = pline.campaign_group_id.campaign_ids[0]
                    code = pline.campaign_group_id.code
                    print "First campaign of group : ", obj.name
                else:
                    obj = pline.campaign_id
                    code = pline.campaign_id.code1

                print "obj : ",obj
#                if not pline.quantity and pline.type_quantity != 'quantity_free' and pline.type_quantity != 'quantity_wanted':
#                    raise  osv.except_osv('Warning', "There's no quantity defined for this purchase line")

                if not pline.product_id.seller_ids:
                    raise  osv.except_osv('Warning', "There's no supplier defined for this product : %s" % (pline.product_id.name,) )

                #create purchase tender
#                tender_desc = 'Purchase Tender for : ' + pline.product_id.name + ' for campaign ' + pline.campaign_id.name
                tender_desc = 'Test'
                tender_id = self.pool.get('purchase.tender').create(cr, uid,{'description':tender_desc,'state':'open'})

                # Create a po / supplier
                for supplier in pline.product_id.seller_ids:
                    partner_id = supplier.id
                    partner = supplier.name

                    address_id = self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default']
                    if not address_id:
                        raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (partner.name,) )
                    delivery_address = address_id
                    pricelist_id = partner.property_product_pricelist_purchase.id
                    if not pricelist_id:
                        raise osv.except_osv('Warning', "There's no purchase pricelist defined for this partner : %s" % (partner.name,) )
                    price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], pline.product_id.id, pline.quantity, False, {'uom': pline.uom_id.id})[pricelist_id]
                    newdate = DateTime.strptime(pline.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=pline.product_id.product_tmpl_id.seller_delay or 0.0)

                    """
                    if not pline.campaign_id.offer_id:
                        raise osv.except_osv('Warning', "There's no offer defined for this campaign : %s" % (pline.campaign_id.name,) )
                    if not pline.campaign_id.proposition_ids:
                        raise osv.except_osv('Warning', "There's no proposition defined for this campaign : %s" % (pline.campaign_id.name,) )
                    """


                    # Get constraints
                    constraints = []
                    if pline.desc_from_offer:
                        print "pline.product_category : ",pline.product_category
                        if int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Mailing Manufacturing')])[0]:
                            for step in obj.offer_id.step_ids:
                                for const in step.manufacturing_constraint_ids:
                                    if not const.country_ids:
                                        constraints.append("---------------------------------------------------------------------------")
                                        constraints.append(const.name)
                                        constraints.append(const.constraint)
                                    elif obj.country_id in const.country_ids:
                                        constraints.append("---------------------------------------------------------------------------")
                                        constraints.append(const.name + ' for country :' +  obj.country_id.name)
                                        constraints.append(const.constraint)
                        elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Item')]):
                            raise osv.except_osv('Warning', "Purchase of items is not yet implemented")
                            for step in obj.offer_id.step_ids:
                                for item in step.product_ids:
                                    constraints.append("---------------------------------------------------------------------------")
                                    constraints.append(item.product_id.name)
                                    constraints.append(item.purchase_constraints)
                        elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Customers File')])[0]:
                                    constraints.append("---------------------------------------------------------------------------")
                                    constraints.append('Campaign Name : %s' % (obj.name,))
                                    constraints.append('Campaign Code : %s' % (obj.code1,))
                                    constraints.append('Deposit Date : %s' % (obj.date_start,))
                                    constraints.append("---------------------------------------------------------------------------")
                                    constraints.append('Trademark : %s' % (obj.trademark_id.name,))
                                    constraints.append('Estimated Quantity : %s' % (obj.quantity_estimated_total,))
    #                                constraints.append('Responsible : %s' % (obj.files_responsible_id.name,))

                                    if obj.files_delivery_address_id:
                                        delivery_address = obj.files_delivery_address_id

                        elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Translation')])[0]:
                            if not obj.lang_id:
                                raise osv.except_osv('Warning', "There's no language defined for this campaign : %s" % (obj.name,) )
                            if pline.notes:
                                constraints.append(pline.notes)
                            else:
                                constraints.append(' ')
                        elif pline.product_category == False:
                            if pline.notes:
                                constraints.append(pline.notes)
                            else:
                                constraints.append(' ')

                    if pline.notes:
                        constraints.append("---------------------------------------------------------------------------")
                        constraints.append(pline.notes)
                    else:
                        constraints.append(' ')

                    # Create po
                    purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                        'origin': code,
                        'partner_id': partner.id,
                        'partner_address_id': address_id,
#                        'dest_address_id': delivery_address.id,
                        'location_id': 1,
                        'pricelist_id': pricelist_id,
                        'notes': "\n".join(constraints),
                        'tender_id': tender_id,
                        'dm_campaign_purchase_line': pline.id
                    })

                    ''' If Translation Order => Get Number of documents in Offer '''
                    if int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Translation')])[0]:
                        print "In translation"
                        quantity=0
                        for step in pline.campaign_id.offer_id.step_ids:
                            quantity += step.doc_number
                        line = self.pool.get('purchase.order.line').create(cr, uid, {
                           'order_id': purchase_id,
                           'name': code,
                           'product_qty': quantity,
                           'product_id': pline.product_id.id,
                           'product_uom': pline.uom_id.id,
                           'price_unit': price,
                           'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                           'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
#                           'account_analytic_id': obj.analytic_account_id,
                        })
                    elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Mailing Manufacturing')])[0]:
                        ''' Create po lines for each proposition (of each campaign if group)'''
                        lines = []
                        if pline.campaign_group_id:
                            print "Creating PO line for group"
                            for campaign in pline.campaign_group_id.campaign_ids:
                                for propo in campaign.proposition_ids:
                                    line_name = propo.code1 + '-' + propo.type
                                    if pline.type_quantity == 'quantity_free':
                                        line_quantity = pline.quantity
                                    elif pline.type_quantity == 'quantity_estimated':
                                        if propo.quantity_estimated.isdigit():
                                            quantity = propo.quantity_estimated
                                        else : 
                                            raise osv.except_osv('Warning',
                                                'Cannot get estimated quantity, check prososition %s' % (propo.name,)) 
                                    elif pline.type_quantity == 'quantity_wanted':
                                        if propo.quantity_wanted.isdigit():
                                            quantity = propo.quantity_wanted
                                        elif propo.quantity_wanted == 'AAA for a Segment':
                                            quantity = 0
                                            line_name = propo.code1 + '-' + propo.type + '- All Addresses Available'
                                        else :
                                            raise osv.except_osv('Warning',
                                                'Cannot get wanted quantity, check prososition %s' % (propo.name,)) 
                                    elif pline.type_quantity == 'quantity_delivered':
                                        if propo.quantity_delivered.isdigit():
                                            quantity = propo.quantity_delivered
                                        else : 
                                            raise osv.except_osv('Warning',
                                                'Cannot get delivered quantity, check prososition %s' % (propo.name,)) 
                                    elif pline.type_quantity == 'quantity_usable':
                                        if propo.quantity_usable.isdigit():
                                            quantity = propo.quantity_usable
                                        else : 
                                            raise osv.except_osv('Warning',
                                                'Cannot get delivered quantity, check prososition %s' % (propo.name,)) 
                                    else:
                                        raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                    line = self.pool.get('purchase.order.line').create(cr, uid, {
                                       'order_id': purchase_id,
                                       'name': line_name,
                                       'product_qty': quantity,
                                       'product_id': pline.product_id.id,
                                       'product_uom': pline.uom_id.id,
                                       'price_unit': price,
                                       'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                       'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                       'account_analytic_id': propo.analytic_account_id,
                                    })
                        else:
                            for propo in obj.proposition_ids:
                                line_name = propo.code1 + '-' + propo.type

                                if pline.type_quantity == 'quantity_free':
                                    line_quantity = pline.quantity
                                elif pline.type_quantity == 'quantity_estimated':
                                    if propo.quantity_estimated.isdigit():
                                        quantity = propo.quantity_estimated
                                    else : 
                                        raise osv.except_osv('Warning',
                                            'Cannot get estimated quantity, check prososition %s' % (propo.name,))
                                elif pline.type_quantity == 'quantity_wanted':
                                    if propo.quantity_wanted.isdigit():
                                        quantity = propo.quantity_wanted
                                    elif propo.quantity_wanted == 'AAA for a Segment':
                                        quantity = 0
                                        line_name = propo.code1 + '-' + propo.type + '- All Addresses Available'
                                    else :
                                        raise osv.except_osv('Warning',
                                            'Cannot get wanted quantity, check prososition %s' % (propo.name,))
                                elif pline.type_quantity == 'quantity_delivered':
                                    if propo.quantity_delivered.isdigit():
                                        quantity = propo.quantity_delivered
                                    else : 
                                        raise osv.except_osv('Warning',
                                            'Cannot get delivered quantity, check prososition %s' % (propo.name,))
                                elif pline.type_quantity == 'quantity_usable':
                                    if propo.quantity_usable.isdigit():
                                        quantity = propo.quantity_usable
                                    else : 
                                        raise osv.except_osv('Warning',
                                            'Cannot get delivered quantity, check prososition %s' % (propo.name,))
                                else:
                                    raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                line = self.pool.get('purchase.order.line').create(cr, uid, {
                                   'order_id': purchase_id,
                                   'name': line_name,
                                   'product_qty': quantity,
                                   'product_id': pline.product_id.id,
                                   'product_uom': pline.uom_id.id,
                                   'price_unit': price,
                                   'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                   'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                   'account_analytic_id': propo.analytic_account_id,
                                })
                    elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Customers File')])[0]:
                        lines = []
                        if pline.campaign_group_id:
                            for campaign in pline.campaign_group_id.campaign_ids:
                                for propo in campaign.proposition_ids:
                                    for segment in propo.segment_ids:
                                        line_name = propo.code1 + ' - ' + segment.list_id.name
                                        if pline.type_quantity == 'quantity_free':
                                            raise osv.except_osv('Warning',
                                                'You cannot use a free quantity for a Customers List order')
                                        elif pline.type_quantity == 'quantity_estimated':
                                            quantity = segment.quantity_estimated
                                        elif pline.type_quantity == 'quantity_wanted':
                                            quantity = segment.quantity_wanted
#                                            if segment.AAA:
                                            if segment.all_add_Avail:
                                                quantity = 0
                                                line_name = propo.code1 + ' - ' + segment.list_id.name + ' - All Addresses Available'
                                        elif pline.type_quantity == 'quantity_delivered':
                                            quantity = segment.quantity_delivered
                                        elif pline.type_quantity == 'quantity_usable':
                                            quantity = segment.quantity_usable
                                        else:
                                            raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                        line = self.pool.get('purchase.order.line').create(cr, uid, {
                                           'order_id': purchase_id,
                                           'name': line_name,
                                           'product_qty': quantity,
                                           'product_id': pline.product_id.id,
                                           'product_uom': pline.uom_id.id,
                                           'price_unit': price,
                                           'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                           'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                           'account_analytic_id': propo.analytic_account_id,
                                        })
                        else:
                            for propo in obj.proposition_ids:
                                for segment in propo.segment_ids:
                                    line_name = propo.code1 + ' - ' + segment.list_id.name
                                    if pline.type_quantity == 'quantity_free':
                                        raise osv.except_osv('Warning',
                                            'You cannot use a free quantity for a Customers List order')
                                    elif pline.type_quantity == 'quantity_estimated':
                                        quantity = segment.quantity_estimated
                                    elif pline.type_quantity == 'quantity_wanted':
                                        quantity = segment.quantity_wanted
#                                        if segment.AAA:
                                        if segment.all_add_avail:
                                            quantity = 0
                                            line_name = propo.code1 + ' - ' + segment.list_id.name + ' - All Addresses Available'
                                    elif pline.type_quantity == 'quantity_delivered':
                                        quantity = propo.quantity_delivered
                                    elif pline.type_quantity == 'quantity_usable':
                                        quantity = propo.quantity_usable
                                    else:
                                        raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                    line = self.pool.get('purchase.order.line').create(cr, uid, {
                                       'order_id': purchase_id,
                                       'name': line_name,
                                       'product_qty': quantity,
                                       'product_id': pline.product_id.id,
                                       'product_uom': pline.uom_id.id,
                                       'price_unit': price,
                                       'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                       'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                       'account_analytic_id': propo.analytic_account_id,
                                    })

                    if pline.type_document == 'po':
                        print "Set as Purchase Order"

                    '''
                    # Set campaign supervision states
                    if pline.type == 'translation':
                        pline.campaign_id.write({'translation_state':'inprogress'})
                    elif pline.type == 'manufacturing':
                        pline.campaign_id.write({'manufacturing_state':'inprogress'})
                    elif pline.type == 'items':
                        pline.campaign_id.write({'items_state':'inprogress'})
                    elif pline.type == 'customer_file':
                        pline.campaign_id.write({'customer_file_state':'inprogress'})
                    '''

        return True

    def _default_date(self, cr, uid, context={}):
        if 'date1' in context and context['date1']:
            dd = context['date1']
            newdate =  DateTime.strptime(dd + ' 09:00:00','%Y-%m-%d %H:%M:%S')
            #print "From _default_date : ",newdate.strftime('%Y-%m-%d %H:%M:%S')
            return newdate.strftime('%Y-%m-%d %H:%M:%S')
        return []


    def _state_get(self, cr, uid, ids, name, args, context={}):
        result = {}
        for pline in self.browse(cr, uid, ids):
            delivered=False
            ordered=False
            if pline.purchase_order_ids:
                for po in pline.purchase_order_ids:
                    if delivered:
                        continue
                    if po.shipped:
                        result[pline.id]='delivered'
                        delivered=True
                        if pline.type == 'translation':
                            trans_id = self.pool.get('dm.offer.translation').create(cr, uid,
                                {'offer_id': pline.campaign_id.offer_id.id,
                                 'date': pline.date_delivery,
                                 'language_id': pline.campaign_id.lang_id.id,
                                 'translator_id':  po.partner_id.id,
                                 'notes': pline.notes,
                                 })
                        continue
                    if ordered:
                        continue
                    if po.state == 'confirmed' or po.state == 'approved':
                        result[pline.id]='ordered'
                        ordered=True
                    if po.state == 'draft':
                        result[pline.id]='requested'
            else:
                result[pline.id] = 'pending'
        return result

    def _delivery_date_get(self, cr, uid, ids, name, args, context={}):
        result = {}
        for pline in self.browse(cr, uid, ids):
            result[pline.id] = False
            for po in pline.purchase_order_ids:
                if po.shipped:
                    if po.picking_ids:
                        result[pline.id] = po.picking_ids[0].date_done
                    continue
        return result

    def onchange_type_quantity(self, cr, uid, ids, type_quantity):
        value = {}
        quantity = 0

#        pline = self.browse(cr, uid, ids)[0]
#        if not pline.campaign_id:
#            raise  osv.except_osv('Warning', "You must first save this Purchase Line and the campaign before using this button")

        print "Quantity Type : ",type_quantity
        """
        print "Parent_type : ",parent_type
        print "Parent_id : ",parent_id
        """
        """
        if pline.campaign_group_id:
            obj = pline.campaign_group_id
        else:
            obj = pline.campaign_id
        """

        if type_quantity == 'quantity_free':
            if not quantity:
                quantity = 0
        elif type_quantity == 'quantity_estimated':
            if obj.quantity_estimated_total.isdigit():
                quantity = obj.quantity_estimated_total
            else :
                raise osv.except_osv('Warning',
                    'Cannot get wanted quantity, check prososition segments')
        elif type_quantity == 'quantity_wanted':
            if obj.quantity_wanted_total.isdigit():
                quantity = obj.quantity_wanted_total
            elif obj.quantity_wanted_total == 'AAA for a Segment':
                quantity = 0
            else :
                raise osv.except_osv('Warning',
                    "Cannot get wanted quantity, check prososition segments")
        elif type_quantity == 'quantity_delivered':
            if obj.quantity_delivered_total.isdigit():
                quantity = obj.quantity_delivered_total
            else :
                raise osv.except_osv('Warning',
                    "Cannot get delivered quantity, check prososition segments")
        elif type_quantity == 'quantity_usable':
            if obj.quantity_usable_total.isdigit():
                quantity = obj.quantity_usable_total
            else :
                raise osv.except_osv('Warning',
                    "Cannot get usable quantity, check prososition segments")
        else:
            raise osv.except_osv('Warning','Error getting quantity')

#        pline.write({'quantity':quantity})
        value['quantity']=quantity

        return {'value':value}

    def _product_category_get(self,cr,uid,context={}):
        type_obj = self.pool.get('product.category')
        dmcat_id = type_obj.search(cr,uid,[('name','ilike','Direct Marketing')])[0]
        type_ids = type_obj.search(cr,uid,[('parent_id','=',dmcat_id)])
        type = type_obj.browse(cr,uid,type_ids)
        return map(lambda x : [str(x.id),x.name],type)

    def _default_category_get(self, cr, uid, *args):
        cr.execute('select id from product_category where name=%s order by id limit 1', ('Mailing Manufacturing',))
        res = cr.fetchone()
        return str(res[0]) or False

    _columns = {
        'campaign_id': fields.many2one('dm.campaign', 'Campaign'),
        'campaign_group_id': fields.many2one('dm.campaign.group', 'Campaign Group'),
        'product_id' : fields.many2one('product.product', 'Product', required=True, context={'flag':True}),
        'quantity' : fields.integer('Total Quantity', readonly=False, required=True),
        'quantity_warning' : fields.char('Warning', size=128, readonly=True),
        'type_quantity' : fields.selection(QTY_TYPES, 'Quantity Type', size=32),
        'type_document' : fields.selection(DOC_TYPES, 'Document Generated', size=32),
        'product_category' : fields.selection(_product_category_get, 'Product Category', size=64 ,select=True),
        'uom_id' : fields.many2one('product.uom','UOM', required=True),
        'date_order': fields.datetime('Order date', readonly=True),
        'date_planned': fields.datetime('Scheduled date', required=True),
        'date_delivery': fields.function(_delivery_date_get, method=True, type='datetime', string='Delivery Date', readonly=True),
        'trigger' : fields.selection(PURCHASE_LINE_TRIGGERS, 'Trigger'),
        'type' : fields.selection(PURCHASE_LINE_TYPES, 'Type'),
        'purchase_order_ids' : fields.one2many('purchase.order','dm_campaign_purchase_line','Campaign Purchase Line'),
        'notes': fields.text('Notes'),
        'togroup': fields.boolean('Apply to Campaign Group'),
        'desc_from_offer' : fields.boolean('Get Description from Offer'),
        'state' : fields.function(_state_get, method=True, type='selection', selection=[
            ('pending','Pending'),
            ('requested','Quotations Requested'),
            ('ordered','Ordered'),
            ('delivered','Delivered'),
            ], string='State', store=True, readonly=True),
    }

    _defaults = {
#        'date_planned' : _default_date,
        'quantity' : lambda *a : 0,
        'uom_id' : _get_uom_id,
        'trigger': lambda *a : 'manual',
        'state': lambda *a : 'pending',
        'type_quantity': lambda *a : 'quantity_wanted',
        'type_document': lambda *a : 'rfq',
        'product_category' : _default_category_get,
        'desc_from_offer': lambda *a : True,
    }
dm_campaign_purchase_line()

class dm_campaign_manufacturing_cost(osv.osv):
    _name = 'dm.campaign.manufacturing_cost'
    _columns = {
        'name' : fields.char('Description', size=64, required=True),
        'amount': fields.float('Amount', digits=(16,2)),
        'campaign_id' : fields.many2one('dm.campaign','Campaign'),
    }
dm_campaign_manufacturing_cost()

class dm_campaign_proposition_prices_progression(osv.osv):
    _name = 'dm.campaign.proposition.prices_progression'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'fixed_prog' : fields.float('Fixed Prices Progression', digits=(16,2)),
        'percent_prog' : fields.float('Percentage Prices Progression', digits=(16,2)),
    }
dm_campaign_proposition_prices_progression()


class Country(osv.osv):
    _name = 'res.country'
    _inherit = 'res.country'
    _columns = {
                'main_language' : fields.many2one('res.lang','Main Language',ondelete='cascade',),
                'main_currency' : fields.many2one('res.currency','Main Currency',ondelete='cascade'),
    }
Country()

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit="res.partner"
    _columns = {
        'country_ids' : fields.many2many('res.country', 'partner_country_rel', 'partner_id', 'country_id', 'Allowed Countries'),
        'state_ids' : fields.many2many('res.country.state','partner_state_rel', 'partner_id', 'state_id', 'Allowed States'),
    }
    def _default_category(self, cr, uid, context={}):
        if 'category_id' in context and context['category_id']:
            return [context['category_id']]
        elif 'category' in context and context['category']:
            id_cat = self.pool.get('res.partner.category').search(cr,uid,[('name','ilike',context['category'])])[0]
            return [id_cat]
        return []

    def _default_all_country(self, cr, uid, context={}):
        id_country = self.pool.get('res.country').search(cr,uid,[])
        return id_country

    def _default_all_state(self, cr, uid, context={}):
        id_state = self.pool.get('res.country.state').search(cr,uid,[])
        return id_state

    _defaults = {
        'category_id': _default_category,
        'country_ids': _default_all_country,
        'state_ids': _default_all_state,
    }
res_partner()

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    _columns = {
        'dm_campaign_purchase_line' : fields.many2one('dm.campaign.purchase_line','DM Campaign Purchase Line'),
    }
purchase_order()

class project_task(osv.osv):
    _name = "project.task"
    _inherit = "project.task"
    context_data ={}

    def default_get(self, cr, uid, fields, context=None):
        if 'type' in context and 'project_id' in context:
            self.context_data = context.copy()
            self.context_data['flag'] = True
        else:
            self.context_data['flag'] = False
        return super(project_task, self).default_get(cr, uid, fields, context)

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        result = super(project_task,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
        if 'flag' in self.context_data or 'type' in context:
            if 'project_id' in self.context_data:
                if result['type']=='form':
                    result['arch']= """<?xml version="1.0" encoding="utf-8"?>\n<form string="Task edition">\n<group colspan="6" col="6">\n<field name="name" select="1"/>\n<field name="project_id" readonly="1" select="1"/>\n
                        <field name="total_hours" widget="float_time"/>\n<field name="user_id" select="1"/>\n<field name="date_deadline" select="2"/>\n<field name="progress" widget="progressbar"/>\n</group>\n
                        <notebook colspan="4">\n<page string="Information">\n<field name="planned_hours" widget="float_time" on_change="onchange_planned(planned_hours,effective_hours)"/>\n<field name="delay_hours" widget="float_time"/>\n
                        <field name="remaining_hours" select="2" widget="float_time"/>\n<field name="effective_hours" widget="float_time"/>\n<field colspan="4" name="description" nolabel="1" select="2"/>\n
                        <field colspan="4" name="work_ids" nolabel="1"/>\n<newline/>\n<group col="11" colspan="4">\n<field name="state" select="1"/>\n<button name="do_draft" states="open" string="Set Draft" type="object"/>
                        <button name="do_open" states="pending,draft" string="Open" type="object"/>\n<button name="do_reopen" states="done,cancelled" string="Re-open" type="object"/>\n<button name="do_pending" states="open" string="Set Pending" type="object"/>\n
                        <button groups="base.group_extended" name="%(project.wizard_delegate_task)d" states="pending,open" string="Delegate" type="action"/>\n<button name="%(project.wizard_close_task)d" states="pending,open" string="Done" type="action"/>\n
                        <button name="do_cancel" states="draft,open,pending" string="Cancel" type="object"/>\n</group>\n</page>\n<page groups="base.group_extended" string="Delegations">\n
                        <field colspan="4" name="history" nolabel="1"/>\n<field colspan="4" height="150" name="child_ids" nolabel="1">\n<tree string="Delegated tasks">\n<field name="name"/>\n
                        <field name="user_id"/>\n<field name="date_deadline"/>\n<field name="planned_hours" widget="float_time"/>\n<field name="effective_hours" widget="float_time"/>\n<field name="state"/>\n</tree>\n
                        </field>\n<field colspan="4" name="parent_id"/>\n</page>\n<page groups="base.group_extended" string="Extra Info">\n<separator string="Planning" colspan="2"/>\n<separator string="Dates" colspan="2"/>\n<field name="priority"/>\n
                        <field name="date_start" select="2"/>\n<field name="sequence"/>\n<field name="date_close" select="2"/>\n<field name="type"/>\n<field name="active" select="2"/>\n
                        <field name="partner_id" select="2"/>\n<separator colspan="4" string="Notes"/>\n<field colspan="4" name="notes" nolabel="1"/>\n</page>\n</notebook>\n</form>"""
        return result
    
    def create(self,cr,uid,vals,context={}):
        if 'flag' in self.context_data:
            if 'type' in self.context_data:
                task_type = self.pool.get('project.task.type').search(cr,uid,[('name','=',self.context_data['type'])])[0]
                vals['type']=task_type
                vals['project_id']=self.context_data['project_id']
                self.context_data = {}
            if 'planned_hours' not in vals:
                vals['planned_hours'] = 0.0
        return super(project_task, self).create(cr, uid, vals, context)
    
    _columns = {
        'date_reviewed': fields.datetime('Reviewed Date'),
        'date_planned': fields.datetime('Planned Date'),
    }

project_task()

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
