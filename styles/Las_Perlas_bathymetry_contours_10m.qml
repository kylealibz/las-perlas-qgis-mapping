<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.44" styleCategories="Symbology|Labeling|Rendering">
  <renderer-v2 type="RuleRenderer" symbollevels="0">
    <rules key="{00000000-0000-0000-0000-000000000001}">
      <rule filter="&quot;depth_m&quot; % 50 = 0" label="50 m contours" symbol="0"/>
      <rule filter="ELSE" label="10 m contours" symbol="1"/>
    </rules>
    <symbols>
      <symbol type="line" name="0" alpha="0.75"><layer class="SimpleLine"><Option type="Map"><Option name="line_color" value="53,105,132,255"/><Option name="line_width" value="0.35"/><Option name="line_width_unit" value="MM"/></Option></layer></symbol>
      <symbol type="line" name="1" alpha="0.50"><layer class="SimpleLine"><Option type="Map"><Option name="line_color" value="92,142,164,255"/><Option name="line_width" value="0.16"/><Option name="line_width_unit" value="MM"/></Option></layer></symbol>
    </symbols>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style fieldName="concat(abs(round(&quot;depth_m&quot;)), ' m')" isExpression="1" fontFamily="Arial" fontSize="7" textColor="46,86,105,255"/>
      <text-format multilineAlign="0" wrapChar="" autoWrapLength="0" useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" reverseDirectionSymbol="0" placeDirectionSymbol="0" formatNumbers="0" decimals="0" plusSign="0"/>
      <placement placement="2" repeatDistance="45" repeatDistanceUnit="MM" preserveRotation="1"/>
      <rendering scaleVisibility="1" maximumScale="0" minimumScale="150000" obstacle="0" drawLabels="1"/>
    </settings>
  </labeling>
  <labelsEnabled>1</labelsEnabled>
</qgis>
