from ui.data import EventLocation

class CurrentView():
    """State class for description current view. This class helps
    switching between views. If histori changes is made, this helper
    can record view settings and switch to it if is neded"""
    
    cfg = None
    
    @classmethod
    def set_cfg(cls, cfg):
        """is file changed"""
        cls.cfg = cfg
    
    def __init__(self, event_location):
        self.diagram_id = self.cfg.diagram_id()
        """Current diagram id"""
        self.tab_id = self.cfg.main_window.regions.currentIndex()
        """Current layer tab id in region panel"""
        self.region_id = self.cfg.main_window.regions.get_current_region()
        """Current region id in region panel"""
        self.diagram_zoom =  self.cfg.diagram.zoom
        """Current diagram zoom"""
        self.diagram_pos_x = self.cfg.diagram.x
        """Current diagram x coordinate"""
        self.diagram_pos_y = self.cfg.diagram.y
        """Current diagram y coordinate"""
        self.event_location = event_location
        """Place where event come"""
        
    def is_compatible(self):
        """Return if current view is compatible with actual state"""
        if self.event_location is EventLocation.layer:
            return True
        elif self.event_location is EventLocation.diagram:
            return self.diagram_id==self.cfg.diagram_id()  
        elif self.event_location is EventLocation.region:
            return True
        raise ValueError("Invalid event location type")
        
    def cmp(self, event_location, first_location):
        """Return if current view is same as actual state"""
        if event_location != first_location:
            return False
        if self.event_location is EventLocation.layer:
            return True
        elif self.event_location is EventLocation.diagram:
            return self.diagram_id==self.cfg.diagram_id()
        elif self.event_location is EventLocation.region:
            return True
        raise ValueError("Invalid event location type")
        
    def set_view(self):
        """Set current view"""   
        self.diagram_id = self.cfg.diagram_id()
        """Current diagram id"""
        old_id =  self.cfg.diagram_id()
        self.cfg.diagrams[self.diagram_id].zoom = self.diagram_zoom
        self.cfg.diagrams[self.diagram_id].x = self.diagram_pos_x
        self.cfg.diagrams[self.diagram_id].y = self.diagram_pos_y
        self.cfg.layers.set_edited_diagram(self.diagram_id)
        self.cfg.set_curr_diagram(self.diagram_id)
        self.cfg.main_window.layers.update()
        self.cfg.main_window.refresh_curr_data(old_id, self.diagram_id)
        
