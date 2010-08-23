// dates.js

var d;	// global used by calendar code

var old_window_onload = window.onload;
window.onload = function()
{
	old_window_onload();	// call any previously specified onload event

	// add show_helper and hide_helper events for input fields
	var start_date = document.getElementById('start_date');
	var end_date = document.getElementById('end_date');
	var datep = document.getElementById('datep');
	var date_span = document.getElementById('date_span');
	start_date.onfocus = function()
	{
		show_helper('datep','start_date');
		update_datep();
	}
	end_date.onfocus = function()
	{
		show_helper('datep','end_date');
		update_datep();
	}
	start_date.onblur = function()
	{
		setTimeout("hide_helper('datep','start_date');",300);
	}
	end_date.onblur = function()
	{
		setTimeout("hide_helper('datep','end_date');",300);
	}
	datep.onclick = function()
	{
		// protect the datep box from being closed while it's being clicked
		document.getElementById('datep').inclick = true;
		setTimeout("document.getElementById('datep').inclick = false;",800);
	}
}	// end window.onload function


function update_datep()
{	
	// fill the date-popup box with the calendar pop-up
	var datep = document.getElementById('datep');
	var helped_el = document.getElementById(datep.helped_field);
	// if date clicked was 1900, use end_date instead
	if (helped_el.value == '1900-01-01')
		helped_el = document.getElementById('end_date');
	var dat = helped_el.value.split('-');
	calendar(dat[0],dat[1],dat[2]);
}


function date_shortcuts()
{
	return '<div id="date_shortcuts">'+
		'<a href="javascript:date_shortcut(\'day\');">today</a> &nbsp; '+
		'<a href="javascript:date_shortcut(\'week\');">week</a> &nbsp; '+
		'<a href="javascript:date_shortcut(\'month\');">month</a> &nbsp; '+
		'<a href="javascript:date_shortcut(\'year\');">year</a></div>';
}


function date_shortcut(period)
{
	// fill in the date shortcut specified, and submit the form
	var start_date = document.getElementById('start_date');
	var end_date = document.getElementById('end_date');
	var ending = new Date();  // today
	var starting = new Date();
	if (period == 'day')
		starting = ending;
	else if (period == 'week')
		starting.setTime(ending.getTime() - 1000 * 60 * 60 * 24 * 7);
	else if (period == 'month')
		starting.setDate(1);
	else if (period == 'year')
	{
		starting.setDate(1);
		starting.setMonth(0);
	}
	start_date.value = to_yyyy_mm_dd(starting);
	end_date.value = to_yyyy_mm_dd(ending);
	hide_helper('datep','');
	document.forms[0].submit();
}	// end function date_shortcut


function to_yyyy_mm_dd(d)
{
	// convert date object to yyyy-mm-dd string
	var ret = d.getFullYear()+'-'
	if (d.getMonth() < 9)
		ret += '0';
	ret += (d.getMonth()+1)+'-';
	if (d.getDate() < 10)
		ret += '0';
	return ret + d.getDate();
}


//       ************************************************************
// THE CODE BELOW IS TAKEN FROM xingguard.com/calendar.js WITH SOME CHANGES
//       ************************************************************
//
//
// simple javascript calendar
//
// requires a div with id "calendar" and an input field with id "date"
//
// calling calendar(year,month) writes a calendar to the div
// specifying the day will highlight that day
// the current day is highlighted by default
//

function calendar_select(day){
	datep = document.getElementById('datep');
	helped_el = document.getElementById(datep.helped_field);
	d.setDate(day);
	helped_el.value = to_yyyy_mm_dd(d);
	hide_helper('datep','');
	document.forms[0].submit();
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

	weekdays = new Array('S','M','T','W','T','F','S');
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

	// add shortcuts above the calendar
	shortcut_html = date_shortcuts();
	document.getElementById('datep').innerHTML=shortcut_html+calendar_html;

	if (typeof highlightDay!='undefined'){
		setTimeout("document.getElementById('"+Math.round(highlightDay)+
			"').className='highlighted';",200);
		delete highlightDay;
	}
}

