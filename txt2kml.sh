#!/usr/bin/env bash
# txt2kml.sh ─ convert every single_TC/*.txt into kml/*.kml
# ------------------------------------------------------------------
# prerequisites: a folder single_TC (holding the split HURDAT2 files)
#                a folder kml        (created automatically)
# usage:  chmod +x txt2kml.sh
#         ./txt2kml.sh
# ------------------------------------------------------------------

outdir="kml"
mkdir -p "$outdir"

# constant for mb → inches of mercury
inHgFactor=0.0295301

for txt in single_TC/*.txt; do
    [ -f "$txt" ] || continue

    # ---- read header (first line) ---------------------------------------
    IFS=',' read -r id rawname rawcount _ <"$txt"
    id=$(echo "$id" | xargs)           # AL282020
    name=$(echo "$rawname" | xargs)    # ZETA
    today=$(date '+%b %d %Y')          # e.g. Jun 27 2025
    kml="$outdir/${txt##*/}"
    kml="${kml%.txt}.kml"              # change extension

    # ---- write fixed prolog & style block ------------------------------
    {
cat <<'BLOCK'
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>ID_REPL</name>
    <open>0</open>

    <!-- =====  Document header ===== -->
    <description><![CDATA[
      <table>
        <tr><td><b>Title:</b> Tropical Cyclone Best Track for ID_REPL</td></tr>
        <tr><td><b>Date Created:</b> DATE_REPL</td></tr>
      </table>
    ]]></description>

    <!-- =====  Styles (ids must be unique)  ===== -->
	<Style id="pt"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>ex_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="cat5"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>cat5_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="db"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>ex_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="cat3"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>cat3_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="ss"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>ts_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="lo"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>ex_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="cat4"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>cat4_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="cat2"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>cat2_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="ts"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>ts_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="cat1"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>cat1_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="ex"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>ex_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="st"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>typhoon_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="tc"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>ex_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="wv"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>ex_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="td"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>td_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="sd"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>ex_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>
	<Style id="ty"> 
		<IconStyle> 
			<scale>1.0</scale> 
			<Icon> 
				<href>typhoon_nhemi.png</href> 
			</Icon> 
             <hotSpot x="15" y="17" xunits="pixels" yunits="pixels"/>
		</IconStyle> 
		<LabelStyle> 
			<scale>1.0</scale> 
		</LabelStyle> 
	</Style>

BLOCK
    } | sed "s/ID_REPL/$id/g; s/DATE_REPL/$today/g" >"$kml"

    # ---- append placemarks ----------------------------------------------
    awk -F',' -v id="$id" -v name="$name" -v factor="$inHgFactor" \
        'function trim(x){sub(/^[ \t]+/,"",x);sub(/[ \t]+$/,"",x);return x}
         function sty(s,w){ # choose style id
             if(s=="TD")return "td";
             if(s=="TS")return "ts";
             if(s=="HU"){
                 if(w>=137)return "cat5";
                 else if(w>=113)return "cat4";
                 else if(w>=96)return "cat3";
                 else if(w>=83)return "cat2";
                 else return "cat1";
             }
             if(s=="EX")return "ex";
             if(s=="SD")return "sd";
             if(s=="SS")return "ss";
             if(s=="DB")return "db";
             if(s=="LO")return "lo";
             if(s=="WV")return "wv";
             return "pt"
         }
         BEGIN{split("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC",mon," ")}
         NR==1{next}                                   # skip header
         {
            date=$1; time=trim($2); flag=trim($3); stat=trim($4)
            latraw=trim($5); lonraw=trim($6)
            wnd=int(trim($7)); pres=int(trim($8))

            # coords
            lat=substr(latraw,1,length(latraw)-1)+0
            if(substr(latraw,length(latraw))=="S")lat=-lat
            lon=substr(lonraw,1,length(lonraw)-1)+0
            if(substr(lonraw,length(lonraw))=="W")lon=-lon

            # time label
            yyyy=substr(date,1,4); mm=int(substr(date,5,2)); dd=int(substr(date,7,2))
            label=sprintf("%s UTC %s %d",time,mon[mm],dd)

            # conversions
            mph=int(wnd*1.15077945+0.5)
            kph=int(wnd*1.852+0.5)
            if(pres==-999){pr_mb="N/A"; pr_in="N/A"}
            else{pr_mb=pres; pr_in=sprintf("%.2f",pres*factor)}

            # build placemark
            print "    <Placemark>"                                >>out
            printf "      <name>%s</name>\n",label                 >>out
            printf "      <styleUrl>#%s</styleUrl>\n",sty(stat,wnd)>>out
            print  "      <description><![CDATA["                  >>out
            print  "        <table>"                               >>out
            printf "          <tr><td>%s %s (%s)</td></tr>\n",stat,name,id >>out
            print  "          <tr><td><hr></td></tr>"              >>out
            printf "          <tr><td>%s</td></tr>\n",label        >>out
            print  "          <tr><td>Storm Location:</td></tr>"   >>out
            printf "          <tr><td><b>%.1f %s, %.1f %s</b></td></tr>\n",\
                   (lat<0?-lat:lat),(lat<0?"S":"N"),(lon<0?-lon:lon),(lon<0?"W":"E") >>out
            print  "          <tr><td>Min Sea Level Pressure:</td></tr>" >>out
            printf "          <tr><td>%s mb / %s in Hg</td></tr>\n",pr_mb,pr_in >>out
            print  "          <tr><td>Maximum Intensity:</td></tr>" >>out
            printf "          <tr><td>%d kt / %d mph / %d kph</td></tr>\n",wnd,mph,kph >>out
            print  "        </table>"                              >>out
            print  "      ]]></description>"                       >>out
            printf "      <Point><coordinates>%g,%g</coordinates></Point>\n",lon,lat >>out
            print  "    </Placemark>"                              >>out
         }' out="$kml" "$txt"

    echo "  </Document>" >>"$kml"
    echo "</kml>"        >>"$kml"
    printf 'created %s\n' "$kml"
done