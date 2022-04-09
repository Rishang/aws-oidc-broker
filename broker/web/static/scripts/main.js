const app = Vue.createApp({
  data() {
    let cli = {}
    return {
      userinfo,
      cli,
      opened: [],
      load_opened: []
    }
  },
  methods: {
    getcli(role, uniqueId) {

      const _load_opened = this.load_opened.indexOf(uniqueId)
      this.load_opened.push(uniqueId)

      let data = axios.get(`/aws?role=${role}&type=cli`)
        .then((response) => {
          return response.data
        })
      // let data = axios.get(`/static/vars.json`)
      //   .then((response) => {
      //     return response.data
      //   })

      data.then((r) => {
        let environment = awsCredHelper(r.Credentials, r.AssumedRoleUser)
        this.dd = r
        // console.log(this.dd)

        this.cli.profile = environment.profile
        this.cli.linux = environment.export.linux
        this.cli.windows = environment.export.windows
        this.cli.account_id = environment.account_id

        // change css
        this.load_opened.splice(_load_opened, 1)
        this.opened = []
        this.opened.push(uniqueId)
      })
    },
    getconsole(role) {
      window.open(`/aws?role=${role}&type=console`, '_blank').focus();

    },
    toggle(uniqueId, array) {
      // console.log(array)
      const index = array.indexOf(uniqueId)
      if (index > -1) {
        array.splice(index, 1)
      } else {
        array.push(uniqueId)
      }
    },
    async copy_clipboard(type) {
      let sucess_message = 'Copied <i class="text-success fa-solid fa-check"></i>'
      let valid_types = ['profile', 'linux', 'windows']

      if (valid_types.includes(type)) {
        navigator.clipboard.writeText(this.cli[type]);
        let temp = document.getElementById(`copy_${type}`).innerHTML
        document.getElementById(`copy_${type}`).innerHTML = sucess_message
        await sleep(3000)
        document.getElementById(`copy_${type}`).innerHTML = temp
      }
    }
  },
  computed: {
    username: function () {
      let username = this.userinfo.preferred_username
      if (username) {
        return username.split('@')[0].replace('_','.').split('.')[0]
      }
      return false
    },
    cli_profile: function () {
      return hljs_html(`${this.cli.profile}`, 'toml')
    },
    cli_linux: function () {
      return hljs_html(`${this.cli.linux}`, 'toml')
    },
    cli_windows: function () {
      return hljs_html(`${this.cli.windows}`, 'toml')
    },
    user_image: function () {
      return `https://avatars.dicebear.com/api/adventurer-neutral/${this.username}.svg`
    }
  }
})

app.mount("#app")

