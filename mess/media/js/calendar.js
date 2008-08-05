// THIS IS THE ORIGINAL CODE FROM xingguard.com/calendar.js


// simple javascript calendar
//
// requires a div with id "calendar" and an input field with id "date"
//
// calling calendar(year,month) writes a calendar to the div
// specifying the day will highlight that day
// the current day is highlighted by default
//
// dates are in the format YYYY/M/D

function calendar_select(day){
	currentDate = document.getElementById('date').value.split("/");
	try{document.getElementById(currentDate[2]).className='day';}
	catch(e){}
	document.getElementById('date').value = d.getFullYear()+'/'+(d.getMonth()+1)+'/'+day;
	document.getElementById(day).className='highlighted';
}

function calendar(year,month,day){
	d = new Date();
	if(typeof year!='undefined')d.setFullYear(year);
	if(typeof month!='undefined')d.setMonth(month-1);
	if(typeof day!='undefined'){d.setDate(day);highlightDay=day;}
        if(typeof year=='undefined')highlightDay=d.getDate();
	month=d.getMonth();
	year=d.getFullYear();
	day=d.getDate();
	nextmonth=month+2;
	prevmonth=month;
	nextyear=year;
	prevyear=year;
	if(month==0){prevmonth=12;prevyear=year-1;}
	if(month==11){nextmonth=1;nextyear=year+1;}

	weekdays = new Array('SU','M','TU','W','TH','F','SA');
	months = new Array('January','February','March','April','May','June','July','August','September','October','November','December');
	month_lengths = new Array(31,28,31,30,31,30,31,31,30,31,30,31);
	if(year%4==0){month_lengths[1]=29;}

	calendar_html='<table class="calendar" cellpadding="2" cellspacing="0"><tr><td class="nav"><a href="javascript:calendar('+prevyear+','+prevmonth+')">&lt;&lt;</a></td><td colspan="5" class="month">'+months[month]+' '+year+'</td><td class="nav"><a href="javascript:calendar('+nextyear+','+nextmonth+')">&gt;&gt;</a></td></tr><tr>';
	for (i=0;i<7;i++) {
		calendar_html+='<td class="weekday" id="'+weekdays[i]+'">'+weekdays[i]+'</td>';
	}
	calendar_html+='</tr><tr>';

	for(i=1;i<=month_lengths[month];i++){
		d.setDate(i);
		iday=d.getDay();
		if(i==1){
			for(j=0;j<iday;j++){
				calendar_html+='<td>&nbsp;</td>';
			}
		}

		if(iday==0 && i!=1) calendar_html+='<tr>';
		calendar_html+='<td id="'+i+'" class="day"><a href="javascript:calendar_select('+i+');">'+i+'</a></td>';
		if(iday==6 || i==month_lengths[month]) calendar_html+='</tr>';
	}
	calendar_html+='</table>';
	document.getElementById('calendar').innerHTML=calendar_html;

	if (typeof highlightDay!='undefined'){
		calendar_select(highlightDay);
		delete highlightDay;
	}

	else {
		current = document.getElementById('date').value.split('/');
		if (typeof current[2]!='undefined'){
			if(current[0]==year && current[1]==month+1)calendar_select(current[2]);
		}
		else {calendar_select(day);}
	}
}
