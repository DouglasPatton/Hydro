from shapely.geometry import Point,Polygon
import descartes
import geopandas as gpd
import pandas as pd
import os
import numpy as np

from bokeh.io import show, output_notebook,curdoc,save, output_file
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Range1d, BBoxTileSource
from bokeh.layouts import row

#add feature to check if multiple CRS conflict
class Sitehucmap():
    '''create map of site and surroundings '''
    def __init__(self, latlon, latlon_crs, sitemetadata):
        self.latlon=latlon
        self.latlon_crs=latlon_crs
        self.sitemetadata=sitemetadata
        self.makemap1()
        
    def extracthuc8(self):
        self.datapath=os.path.join(self.sitedirectory,urlsuffix+'.xml')#put these details in a companion file and simplify file name
        if os.path.exists(self.datapath):
            self.data=ET.parse(self.datapath) #add try clause?
            self.root=self.data.getroot() 
        else:    
            response=urlopen(Request(self.requesturl,headers={"Accept-Encoding": "gzip"})) 
            self.data=gzip.open(response, 'rb').read()
            self.root=ET.fromstring(self.data)
            savefile=open(self.datapath,'w')
            savefile.write(ET.tostring(self.root).decode("utf-8"))
            savefile.close()
        
    def makemap1(self):    
        seriescount=len(self.latlon)
        
        
        df=pd.DataFrame([[float(self.latlon[j][-11:]),float(self.latlon[j][:11]),self.latlon_crs[j],self.sitemetadata[j]] for j in range(seriescount)],columns=["longitude","latitude","CRS","site_name"])
        geometry=[Point((df['longitude'][i],df['latitude'][i])) for i in range(seriescount)]
        gdf=gpd.GeoDataFrame(df, geometry=geometry, crs={'init':self.latlon_crs[0].lower()})
                
       
        self.gdf=gdf
        
        # project to merkator
        gdf_merk=gdf.copy().to_crs({'init':'epsg:3395'})
        
        self.gdf_merk=gdf_merk
                #find max and min lat and lon and plan data request.
        #help from and thanks to: https://github.com/bokeh/bokeh/issues/7825
        xy=[(point.x,point.y) for point in gdf_merk.geometry]
        #print(xy)
        latlist=[xy[i][1] for i in range(seriescount)]
        lonlist=[xy[i][0] for i in range(seriescount)]
        
        #print(latlist,lonlist)
        latarray=np.asarray(latlist)
        lonarray=np.asarray(lonlist)
        
        latmin=np.amin(latarray)
        latmax=np.amax(latarray)
        lonmin=np.amin(lonarray)
        lonmax=np.amax(lonarray)
        
        buffer=10000000
        latrange=latmax-latmin
        if latrange<buffer: latrange=buffer
        lonrange=lonmax-lonmin
        if lonrange<buffer: lonrange=buffer
        
        #print(lonmin,lonmax,lonrange)
        bscale=.7
        xmin=lonmin-lonrange**bscale
        xmax=lonmax+lonrange**bscale
        ymin=latmin-latrange**bscale
        ymax=latmax+latrange**bscale
        #print('xmin',xmin,'xmax',xmax,'ymin',ymin,'ymax',ymax)

    
        
        '''https://basemap.nationalmap.gov/arcgis/services/'
       'USGSTopo/MapServer/WMSServer?service=WMS&'
       'request=GetMap&version=1.3.0&BGCOLOR=0xFFFFFF&&format=image/png&'
       'crs={crs}&layers={layer}&width={width}&height={height}')
         url.format(crs=crs, width=width, height=height, layer=layer) + \
          '&bbox={XMIN},{YMIN},{XMAX},{YMAX}'''
        
        basewmsurl1=('https://smallscale.nationalmap.gov/arcgis/services/LandCover/MapServer/WMSServer?service=WMS&'
                    'request=GetMap&version=1.3.0&BGCOLOR=0xFFFFFF&&format=image/png')
        basewmsurl=('https://basemap.nationalmap.gov/arcgis/services/USGSTopo/MapServer/WMSServer?service=WMS&'
                    'request=GetMap&version=1.3.0&BGCOLOR=0xFFFFFF&&format=image/png')
        
        
        crs='&crs={crs}'.format(crs='EPSG:3395')
        styles='&styles='
        styles1='&styles=default'
        layers='&layers={layer}'.format(layer='0')
        layers1='&layers={layer}'.format(layer='1')
        width='&width={width}'.format(width=256)
        height='&height={height}'.format(height=256)
        bbox='&bbox={XMIN},{YMIN},{XMAX},{YMAX}'
        #self.wmsurl=basewmsurl+styles+crs+layers+width+height+bbox
        self.wmsurl=basewmsurl1+styles1+crs+layers1+width+height+bbox
       # 'https://smallscale.nationalmap.gov/arcgis/services/LandCover/MapServer/WMSServer?request=GetCapabilities&service=WMS
        #next ~30 lines copied from above source.
        x_range = Range1d(start=xmin, end=xmax, bounds=None)
        y_range = Range1d(start=ymin, end=ymax, bounds=None)

        fig = figure(x_range=x_range,
                      lod_threshold=None,
                      plot_width=500,
                      plot_height=300,
                      background_fill_color='white',
                      y_range=y_range,)
        fig.axis.visible = False
        fig.toolbar_location = 'above'

        tile_source = BBoxTileSource(url=self.wmsurl)
        fig.add_tile(tile_source)
        
        source = ColumnDataSource(
            data=dict(lat=latlist,
                      lon=lonlist)
        )

        fig.circle(x="lon", y="lat", size=15, fill_color="blue", fill_alpha=0.8,
                   source=source)
        '''layout = row(fig)
        curdoc().add_root(layout)
        curdoc().title = "WMS Viewer"  
        '''
        #show(fig)
        #save(fig,filename='map1')
        self.fig=fig
