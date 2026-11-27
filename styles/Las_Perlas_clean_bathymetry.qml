<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.44" styleCategories="Symbology|Rendering">
  <pipe>
    <rasterrenderer type="singlebandpseudocolor" band="1" opacity="0.88" classificationMin="-130" classificationMax="0">
      <rasterTransparency/>
      <minMaxOrigin><limits>MinMax</limits><extent>WholeRaster</extent><statAccuracy>Estimated</statAccuracy><cumulativeCutLower>0.02</cumulativeCutLower><cumulativeCutUpper>0.98</cumulativeCutUpper><stdDevFactor>2</stdDevFactor></minMaxOrigin>
      <rastershader>
        <colorrampshader colorRampType="INTERPOLATED" classificationMode="1" clip="1" minimumValue="-130" maximumValue="0" labelPrecision="0">
          <colorramp name="[source]" type="gradient">
            <Option type="Map"><Option name="color1" value="18,72,115,255"/><Option name="color2" value="235,248,252,255"/><Option name="discrete" value="0"/></Option>
          </colorramp>
          <item value="-130" label="130 m" color="#124873" alpha="255"/>
          <item value="-100" label="100 m" color="#1f6594" alpha="255"/>
          <item value="-75" label="75 m" color="#3988b4" alpha="255"/>
          <item value="-50" label="50 m" color="#70b2d0" alpha="255"/>
          <item value="-25" label="25 m" color="#b5dce9" alpha="255"/>
          <item value="0" label="0 m" color="#ebf8fc" alpha="255"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0" gamma="1"/>
    <huesaturation colorizeOn="0" grayscaleMode="0" saturation="0"/>
    <rasterresampler maxOversampling="4"><zoomedInResampler type="cubic"/><zoomedOutResampler type="average"/></rasterresampler>
  </pipe>
</qgis>
