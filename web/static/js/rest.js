// // POST method - send image of dog to back-end
$(function() {
    $('#btnSubmit').click(function() {
        var data=new FormData()
          data.append('file',$("#file-upload")[0].files[0])

          $.ajax({
              url:"/tf_breed",
              type:'POST',
              data:new FormData($("#upload-form")[0]),
              cache:false,
              processData:false,
              contentType:false,
              error:function(error){
                  console.log("upload error")
                  console.log(error)
              },
              success:function(data){
                  console.log(data)
                  console.log("upload success")
                  $("#retrieve_breed").html("<p>Best guess: "+data.breed.breed+" - "+data.breed.result+"%</p>");
              }
          })
    });
});