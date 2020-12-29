function addNewChat(direction, text) {
  var mytext = text;
  var textnode;
  var node;
  var node2;
  var node3;
  if (direction =="fromBot") {
      textnode = document.createTextNode(mytext);
          p_node = document.createElement("p");
          p_node.appendChild(textnode);
       
          img_node = document.createElement("img");
          img_node.classList.add("bot-avatar");
       
          li_node = document.createElement("li");
          li_node.classList.add("w3-animate-zoom");
          li_node.classList.add("incoming_msg");
          li_node.appendChild(img_node);
          li_node.appendChild(p_node);
          document.getElementById("msg_history").appendChild(li_node);
    }
   else {
          textnode = document.createTextNode(mytext);
          p_node = document.createElement("p");
          p_node.appendChild(textnode);
       
          
       
          li_node = document.createElement("li");
          li_node.classList.add("outgoing_msg");
          li_node.appendChild(p_node);
          document.getElementById("msg_history").appendChild(li_node);
       
          
   
   }
}

function stars_reset(){
    $('#star1 a').first().nextAll("a").removeClass("fa-star").addClass("fa-star-o");
    $('#selected_star').text("1");
}
$('#star1 a').click(function(){
    $(this).nextAll().removeClass("fa-star").addClass("fa-star-o").end().addClass("fa-star").removeClass("fa-star-o").prevAll().addClass("fa-star").removeClass("fa-star-o");
    var x = $(this).index();
    $('#selected_star').text(x+1);
    
  });


// $('.outgoing_msg').last().nextAll(".received_msg")

//-----------------
//Rating Stars and get value of rating
$('#star2').starrr({
    rating: 1,
    change: function (e, value) {
        if (value) {
            $('.your-choice-was').show();
            $('.choice').text(value);//print value of rating to text
            //var v = $('#hInput').val().split(",");// there is hidden input which has value of user,bot,rating 
            v[v.length - 1] = value;
            //$('#hInput').val(v);//make the rating in last element of hidden element
            //console.log($('#hInput').val())
        } else {
            $('.your-choice-was').hide();//hide rating div
        }
    }
});
//-----------------
//ajax and draw both request and output in chat
function getBotResponse() {
    $('#th').hide();//hide thank you text if it's shown
    $('#ple').show();//Show please evaluate text 
    var humandata = $("#btn-input").val();//take user input at chat
    
    $("#btn-input").val('');
    addNewChat("fromUser", humandata )
    //document.getElementById('userInput').scrollIntoView({block: 'start', behavior: 'smooth'});
    
    let mydata = {};
    mydata["data"] = humandata;
    
    req = $.ajax({
        type: "POST",
        url: '/chat',
        data: JSON.stringify(mydata),
        dataType: 'json'
    }).done(function (data) {
        bot_reply = data;
        //console.log("data" + data['response']);
        console.log(data.length);
        
        var msg_box = document.getElementById("msg_history");
        data.forEach(function(e){ console.log(e) });
        data.forEach(function(e,index){ setTimeout(function () {   //  we us index here to solve issue of settimerout not work in foreach loop
                                            addNewChat("fromBot", e);
                                            msg_box.scrollTop = msg_box.scrollHeight;
                                    }, (index+1)*500) 
                                
        });
        
       // myObj = JSON.parse(bot_reply);
        //consol.log(myObj[0]);
        
        //lo = data['response'].replace(/'/g, '').replace('[', '').replace(']', '').split(",");
        //var i = 0;                  //  set your counter to 0

        
        
        //$("#rate").show();//show rate panel
        $("#msg_to_user").hide();
        $("#receive_evaluation").show();
        
        $("#btn-chat").prop("disabled", true);//disable inputs
        $("#btn-input").prop("disabled", true);
        $("#btn-input").attr("placeholder", "please evaluate bot reply before enter new MSG");


    });
}
//-----------------
//trigger ajax function by button or press return
$("#btn-chat").click(getBotResponse)
$("#btn-input").keypress(function (e) {
    if ((e.which == 13) && document.getElementById("btn-input").value != "") {
        console.log('en');

        $("#btn-chat").click()

    }
});
//-----------------
//send final data to db
function sendEdit() {//function to send data to api to be commited in the database
    const last_sent = $('#msg_history').children('li.outgoing_msg').last().text();
    last_reply = $('#msg_history').children('li.outgoing_msg').last().nextAll(".incoming_msg").map(function(i,el) {
    return $(el).text();
    }).get();
    var reply_evaluation = $('.choice').text();//print value of rating to text
    console.log(last_sent);
    //var data_to_send_list;
    var data_to_send_list = {"sent":last_sent, "reply":last_reply, "evaluation":reply_evaluation}
    //data_to_send_list["sent"] = last_sent;
    //data_to_send_list["reply"] = last_reply;
    //data_to_send_list["evaluation"] = reply_evaluation;
    var data_to_be_sent = {"data": data_to_send_list }
    //data_to_be_sent["data"]= data_to_send_list;
    josn_data = JSON.stringify(data_to_be_sent);
    console.log(josn_data);
    //var rd = $('#hInput').val();//get hidden input value
   // $('#hInput').val('user,bot,1');//re-set the value of hidden input
   // console.log(rd)
    req = $.ajax({//post values of hidden input before reset to server
        type: "POST",
        url: '/SaveChat',
      //  data: JSON.stringify(rd),
        data: josn_data,
        dataType: 'json'
    }).done(function (data) {
        $('#th').show();//display thank you after data is commited
        $('#ple').hide();//hide please evaluate
        console.log(data);
        setTimeout(function () {//hide rate panel after 2 seconds and enable inputs so user can write more data
            //$('.your-choice-was').hide();
            //$("#rate").hide();
            $("#btn-chat").prop("disabled", false);
            $("#btn-input").prop("disabled", false);
            $("#msg_to_user").show();
            $("#receive_evaluation").hide();
            stars_reset();
            $("#btn-input").attr("placeholder", "Type a message").focus();
            //$("input").focus();
        }, 200);
        
    });


};
//-----------------