const sstk = require("shutterstock-api");
const process = require("process");
sstk.setAccessToken(process.env.SHUTTERSTOCK_API_TOKEN);
console.log(process.env.SHUTTERSTOCK_API_TOKEN);
const usersApi = new sstk.UsersApi();

usersApi.getUser()
  .then((data) => {
    console.log(data);
  })
  .catch((error) => {
    console.error(error);
  });