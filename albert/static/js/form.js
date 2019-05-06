$(document).ready(function() {
  $("#registerForm").on("submit", function(event) {
    $("#loader2").show();

    $.ajax({
      data: {
        name: $("#nameInput").val(),
        surname: $("#surnameInput").val(),
        email: $("#emailInput").val()
      },
      type: "POST",
      url: "/process"
    }).done(function(data) {
      if (data.error) {
        $("#errorAlert")
          .text(data.error)
          .show();

        $("#successAlert").hide();
      } else {
        $("#loader2").hide();
        var messagesContainer = $(".messages");
                    newMessage = "about";
                    console.log(newMessage);
                    messagesContainer.append(
                        ['<li class="self">', data.name, "</li>"].join("")
                    );
       
      }
    });

    event.preventDefault();
  });
});

$(document).ready(function() {
  $("#contactUs").on("submit", function(event) {
    $.ajax({
      data: {
        name: $("#userName").val(),
        surname: $("#userEmail").val(),
        email: $("#userPhone").val(),
        website: $("#userWebsite").val(),
        message: $("#userMessage").val()
      },
      type: "POST",
      url: "/send-mail"
    }).done(function(data) {
      if (data.error) {
        $("#errorAlert")
          .text(data.error)
          .show();
        $("#successAlert").hide();
      } else {
        $("#successAlert")
          .text(data.name)
          .show();
        $("#errorAlert").hide();
      }
    });

    event.preventDefault();
  });
});
