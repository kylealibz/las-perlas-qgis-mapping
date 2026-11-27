import os
from pathlib import Path
from qgis.core import (
    QgsApplication, QgsProject, QgsCoordinateReferenceSystem, QgsRasterLayer,
    QgsVectorLayer, QgsRectangle, QgsRasterShader, QgsColorRampShader,
    QgsSingleBandPseudoColorRenderer, QgsRuleBasedRenderer, QgsMarkerSymbol,
    QgsLineSymbol, QgsFillSymbol, QgsPalLayerSettings, QgsVectorLayerSimpleLabeling,
    QgsTextFormat, QgsTextBufferSettings, QgsLayout, QgsPrintLayout, QgsLayoutItemMap,
    QgsLayoutItemLabel, QgsLayoutItemScaleBar, QgsLayoutPoint, QgsLayoutSize,
    QgsUnitTypes, QgsLayoutExporter, QgsLayoutItemShape, QgsLayoutItemPicture,
    QgsLayoutMeasurement, QgsReadWriteContext, Qgis
)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import QRectF

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data"
QGIS_ROOT = REPO_ROOT / "qgis"
OUTPUT_ROOT = REPO_ROOT / "outputs"

# Used only when the script is run from a standalone QGIS Python environment.
# When executed from the QGIS Python Console, an application instance already
# exists and this value is ignored.
QGIS_PREFIX = os.environ.get(
    "QGIS_PREFIX_PATH",
    r"C:\Program Files\QGIS 3.44.12\apps\qgis-ltr",
)

QGIS_ROOT.mkdir(exist_ok=True)
OUTPUT_ROOT.mkdir(exist_ok=True)

app = QgsApplication.instance()
owns_app = app is None
if owns_app:
    app = QgsApplication([], False)
    app.setPrefixPath(QGIS_PREFIX, True)
    app.initQgis()
project = QgsProject.instance()
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
project.setTitle("Las Perlas Archipelago BRUV survey sites")
project.setFilePathStorage(Qgis.FilePathType.Relative)

def add_raster(name, filename):
    lyr = QgsRasterLayer(str(DATA_ROOT / filename), name)
    if not lyr.isValid(): raise RuntimeError(f"Invalid raster: {filename}")
    project.addMapLayer(lyr)
    return lyr

def add_vector(name, source, provider="ogr"):
    lyr = QgsVectorLayer(source, name, provider)
    if not lyr.isValid(): raise RuntimeError(f"Invalid vector: {source}")
    project.addMapLayer(lyr)
    return lyr

def style_bathy(layer):
    shader = QgsRasterShader()
    ramp = QgsColorRampShader(-130, 0)
    ramp.setColorRampType(QgsColorRampShader.Interpolated)
    ramp.setClip(True)
    ramp.setColorRampItemList([
        QgsColorRampShader.ColorRampItem(-130, QColor("#2f6686"), "130 m"),
        QgsColorRampShader.ColorRampItem(-100, QColor("#4d83a2"), "100 m"),
        QgsColorRampShader.ColorRampItem(-75, QColor("#73a6bd"), "75 m"),
        QgsColorRampShader.ColorRampItem(-50, QColor("#a4c8d5"), "50 m"),
        QgsColorRampShader.ColorRampItem(-25, QColor("#d2e6ea"), "25 m"),
        QgsColorRampShader.ColorRampItem(0, QColor("#eef6f5"), "0 m"),
    ])
    shader.setRasterShaderFunction(ramp)
    renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
    renderer.setClassificationMin(-130); renderer.setClassificationMax(0)
    layer.setRenderer(renderer); layer.setOpacity(0.96)

def style_land(layer):
    shader = QgsRasterShader(); ramp = QgsColorRampShader(1, 1)
    ramp.setColorRampType(QgsColorRampShader.Exact)
    ramp.setColorRampItemList([QgsColorRampShader.ColorRampItem(1, QColor("#e8e8e3"), "Land")])
    shader.setRasterShaderFunction(ramp)
    layer.setRenderer(QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader))

def style_sites(layer):
    root = QgsRuleBasedRenderer.Rule(None)
    colors = {"Coral/Algae":"#009E8E", "Rock":"#30343B", "Rubble":"#8D99AE", "Sand":"#E6A92F"}
    for habitat, color in colors.items():
        for use, shape, size in [("Base", "circle", 2.4), ("Over", "triangle", 2.8)]:
            sym = QgsMarkerSymbol.createSimple({
                "name": shape, "color": color, "size": str(size),
                "outline_color": "#ffffff", "outline_width": "0.45"
            })
            rule = QgsRuleBasedRenderer.Rule(sym)
            rule.setLabel(f"{habitat} — {'base' if use == 'Base' else 'oversample'}")
            rule.setFilterExpression(f'"habitat" = \'{habitat}\' AND "siteuse" = \'{use}\'')
            root.appendChild(rule)
    layer.setRenderer(QgsRuleBasedRenderer(root))

def set_labels(layer, field, size=8, color="#30343b", buffer=1.1):
    s = QgsPalLayerSettings(); s.fieldName = field; s.enabled = True
    s.placement = QgsPalLayerSettings.AroundPoint
    fmt = QgsTextFormat(); fmt.setFont(QFont("Arial", size)); fmt.setSize(size); fmt.setColor(QColor(color))
    b = QgsTextBufferSettings(); b.setEnabled(True); b.setSize(buffer); b.setColor(QColor("#ffffff")); fmt.setBuffer(b)
    s.setFormat(fmt); layer.setLabeling(QgsVectorLayerSimpleLabeling(s)); layer.setLabelsEnabled(True)

bathy = add_raster("Bathymetry (GMRT, metres)", "Las_Perlas_clean_bathymetry.tif"); style_bathy(bathy)
land = add_raster("Land", "Las_Perlas_land_mask.tif"); style_land(land)
coast = add_vector("Coastline", str(DATA_ROOT / "Las_Perlas_coastline.gpkg"))
coast.setRenderer(QgsRuleBasedRenderer(QgsRuleBasedRenderer.Rule(QgsLineSymbol.createSimple({"color":"#626b70","width":"0.32"}))))
contours = add_vector("Depth contours (10 m)", str(DATA_ROOT / "Las_Perlas_bathymetry_contours_10m.gpkg"))
contours.setRenderer(QgsRuleBasedRenderer(QgsRuleBasedRenderer.Rule(QgsLineSymbol.createSimple({"color":"#5f91a4","width":"0.16","line_style":"solid"}))))
contours.setOpacity(0.50)

csv = str(DATA_ROOT / "Las_Perlas_GRTS_sites.csv").replace("\\", "/")
sites = add_vector("GRTS survey sites", f"file:///{csv}?delimiter=,&xField=lon&yField=lat&crs=EPSG:4326", "delimitedtext")
style_sites(sites)

countries = add_vector("Locator countries", str(DATA_ROOT / "locator_countries.geojson"))
countries.setRenderer(QgsRuleBasedRenderer(QgsRuleBasedRenderer.Rule(QgsFillSymbol.createSimple({"color":"#e5e5e2","outline_color":"#7a7f82","outline_width":"0.25"}))))
set_labels(countries, "name", 7, "#52575a", 0.8)

# Editable island labels, stored inside the project.
labels = QgsVectorLayer("Point?crs=EPSG:4326&field=name:string", "Island labels", "memory")
dp = labels.dataProvider()
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY
for name, x, y in [
    ("Contadora",-79.033,8.635), ("Saboga",-79.020,8.586), ("Pedro González",-79.108,8.402),
    ("Isla del Rey",-78.915,8.345), ("Isla San José",-79.104,8.198), ("Gulf of Panama",-78.790,8.610)
]:
    f=QgsFeature(labels.fields()); f.setAttribute("name",name); f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x,y))); dp.addFeature(f)
labels.updateExtents(); project.addMapLayer(labels); set_labels(labels, "name", 8, "#26343b", 1.2)

layout = QgsPrintLayout(project); layout.initializeDefaults(); layout.setName("Figure 1 - Study site map")
pc = layout.pageCollection(); page = pc.page(0); page.setPageSize(QgsLayoutSize(210, 245, QgsUnitTypes.LayoutMillimeters))

def label(text, x, y, w, h, size=9, bold=False, color="#26343b", align=0):
    it=QgsLayoutItemLabel(layout); it.setText(text); f=QFont("Arial",size); f.setBold(bold); it.setFont(f); it.setFontColor(QColor(color))
    it.attemptMove(QgsLayoutPoint(x,y,QgsUnitTypes.LayoutMillimeters)); it.attemptResize(QgsLayoutSize(w,h,QgsUnitTypes.LayoutMillimeters)); layout.addLayoutItem(it); return it

def panel_map(x,y,w,h,extent,layers,title,letter,grid=True):
    m=QgsLayoutItemMap(layout); m.attemptMove(QgsLayoutPoint(x,y,QgsUnitTypes.LayoutMillimeters)); m.attemptResize(QgsLayoutSize(w,h,QgsUnitTypes.LayoutMillimeters))
    m.setFrameEnabled(True); m.setFrameStrokeColor(QColor("#4f5558")); m.setFrameStrokeWidth(QgsLayoutMeasurement(0.35,QgsUnitTypes.LayoutMillimeters))
    m.setLayers(layers); m.setExtent(QgsRectangle(*extent)); layout.addLayoutItem(m)
    if grid:
        g=m.grid(); g.setEnabled(True); g.setIntervalX(0.1); g.setIntervalY(0.1); g.setStyle(g.FrameAnnotationsOnly); g.setAnnotationEnabled(True); g.setAnnotationPrecision(1)
        g.setAnnotationFont(QFont("Arial",6)); g.setAnnotationFontColor(QColor("#555b5e")); g.setFrameStyle(g.ExteriorTicks); g.setFrameWidth(1.4)
    label(letter, x+2, y+1, 6, 5, 9, True)
    label(title, x+10, y+1, w-12, 5, 8, True)
    return m

label("Las Perlas Archipelago BRUV survey sites", 10, 5, 190, 9, 16, True, "#20323b")
label("Gulf of Panama · spatially balanced sampling stratified by benthic habitat", 10, 14, 190, 6, 8, False, "#5a6971")

locator = panel_map(10,23,74,65,(-83.2,7.0,-76.8,10.3),[countries],"Regional location","a",False)
overview = panel_map(87,23,113,65,(-79.18,8.15,-78.74,8.67),[labels,sites,coast,land,contours,bathy],"Las Perlas Archipelago","b",True)
north = panel_map(10,91,93,91,(-79.17,8.385,-78.76,8.67),[labels,sites,coast,land,contours,bathy],"Northern survey region","c",True)
south = panel_map(106,91,94,91,(-79.17,8.15,-78.78,8.44),[labels,sites,coast,land,contours,bathy],"Southern survey region","d",True)

# Locator study-area box as a red frame placed geographically over Panama Gulf.
box_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "Study-area locator", "memory")
bf=QgsFeature(); bf.setGeometry(QgsGeometry.fromRect(QgsRectangle(-79.25,8.05,-78.65,8.75))); box_layer.dataProvider().addFeature(bf); project.addMapLayer(box_layer)
box_layer.setRenderer(QgsRuleBasedRenderer(QgsRuleBasedRenderer.Rule(QgsFillSymbol.createSimple({"color":"255,255,255,0","outline_color":"#d64545","outline_width":"0.8"}))))
locator.setLayers([box_layer,countries])

def scale_bar(map_item,x,y,segments=2,units_per=5):
    s=QgsLayoutItemScaleBar(layout); s.setLinkedMap(map_item); s.setStyle("Single Box"); s.setUnits(QgsUnitTypes.DistanceKilometers)
    s.setNumberOfSegments(segments); s.setNumberOfSegmentsLeft(0); s.setUnitsPerSegment(units_per); s.setHeight(1.5); s.setFont(QFont("Arial",6)); s.setUnitLabel("km")
    s.attemptMove(QgsLayoutPoint(x,y,QgsUnitTypes.LayoutMillimeters)); s.attemptResize(QgsLayoutSize(28,7,QgsUnitTypes.LayoutMillimeters)); layout.addLayoutItem(s)
scale_bar(locator, 14,78,2,100); scale_bar(overview,91,78,2,10); scale_bar(north,14,171,2,5); scale_bar(south,110,171,2,5)
label("N\n▲", 191, 27, 7, 12, 8, True, "#27343a")

# Clean, manually composed legend matching the example.
label("Survey sites",10,187,35,5,9,True)
label("●  Base site (n = 60)",10,194,42,5,7,False,"#30343b")
label("▲  Oversample (n = 20)",10,200,48,5,7,False,"#30343b")
label("Benthic habitat",61,187,38,5,9,True)
legend_items=[("■","Coral/Algae","#009E8E"),("■","Rock","#30343B"),("■","Rubble","#8D99AE"),("■","Sand","#E6A92F")]
for i,(sym,txt,col) in enumerate(legend_items): label(f"{sym}  {txt}",61+(i%2)*37,194+(i//2)*6,36,5,7,False,col)
label("Bathymetry",139,187,30,5,9,True)
for i,(col,txt) in enumerate([("#eef6f5","0 m"),("#a4c8d5","50 m"),("#4d83a2","100 m"),("#2f6686","130 m")]):
    sh=QgsLayoutItemShape(layout); sh.setShapeType(QgsLayoutItemShape.Rectangle); sh.attemptMove(QgsLayoutPoint(139+i*14,194,QgsUnitTypes.LayoutMillimeters)); sh.attemptResize(QgsLayoutSize(14,4,QgsUnitTypes.LayoutMillimeters));
    sh.setSymbol(QgsFillSymbol.createSimple({"color":col,"outline_style":"no"})); layout.addLayoutItem(sh); label(txt,139+i*14,198,14,4,5,False,"#4d5960")

label("Figure 1. Location of 80 GRTS-selected BRUV sites in the Las Perlas Archipelago, Gulf of Panama. Circles indicate base sites and triangles indicate oversamples; colours represent benthic-habitat strata. Bathymetric contours are shown at 10 m intervals.",10,211,190,14,7,False,"#34444c")
label("Data: GMRT v4.5 bathymetry; Natural Earth country boundaries; Las_Perlas_GRTS_sites.csv. CRS: WGS 84 (EPSG:4326).",10,229,190,6,6,False,"#65737a")

project.layoutManager().addLayout(layout)
qgz=str(QGIS_ROOT / "Las_Perlas_BRUV_Publication_Map.qgz"); project.write(qgz)
png=str(OUTPUT_ROOT / "Figure_1_Las_Perlas_study_site_map.png")
pdf=str(OUTPUT_ROOT / "Figure_1_Las_Perlas_study_site_map.pdf")
settings=QgsLayoutExporter.ImageExportSettings(); settings.dpi=300
QgsLayoutExporter(layout).exportToImage(png,settings)
ps=QgsLayoutExporter.PdfExportSettings(); ps.dpi=300
QgsLayoutExporter(layout).exportToPdf(pdf,ps)
print(qgz); print(png); print(pdf)
if owns_app:
    app.exitQgis()
else:
    from qgis.PyQt.QtCore import QTimer
    QTimer.singleShot(500, app.quit)
