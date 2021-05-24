# Performance dashboard

A performance dashboard generator that lets you host a dashboard which show others how your servers perform. Since it uses Github pages hosting is all for free. It uses [Server Density](https://www.serverdensity.com/?utm_campaign=perf-dashboard&utm_source=github&medium=repo) to pull metrics from your servers, however PRs are welcome to integrate with other metrics solutions. You can see what our dashboard looks like [here](https://stats.serverdensity.com).

## A short demo
![Demo](/docs/demo.gif "Demo")

## Future Features
Open an issue to let us know what kind of features you would like to see. If you are of the creative kind, take a look at the issues and implement a feature!  

Things that could make sense in the future. 

    - Save historic data so it can be displayed in a timeline. 
    - UI interface interface for configuration instead of yaml


## Installation
The very first thing you should do is to FORK this project. Once you've forked it you can start customizing your settings. 

To be able to get data from your server in the first place you need to monitor your server with Server Density. So go ahead and [sign up for an account](https://www.serverdensity.com/?utm_campaign=perf-dashboard&utm_source=github&medium=repo) at Server Density. (Feel free to make PRs to make this work with other monitoring solutions).

The next step is to start configuring your `conf.yml` to be able to fetch data. Use `conf_dev.yml` as a starting point for your configurations or our own configuration in `conf.yml`. The first step would be to create barebone configuration that contains the groups and tags that you want to fetch data from. Then run `make available`. 

```
infrastructure:
    - title: A funky title
      group: my-group
    - title: My awesome server
      tag: my-tag
```

That will create a file `available.md` with all the metrics each group or tag has<sup>[1](#myfootnote1)</sup>. 

That file will look something like this. From here you can see what metrics you find interesting and then go on and copy the `metrickey` to each metrics in `conf.yml` 
```
    # Available metrics for all your groups

    ##API Load Balancers
    ###Top Processes python (sd-agent) Processes
    metrickey: topProcesses.python (sd-agent).p

    ###Top Processes python (sd-agent) CPU
    metrickey: topProcesses.python (sd-agent).c

    <snip>
```

Once you're happy with the configuration you can run `make generate` to generate the performance dashboard. This will create an output folder where `index.html` exists which is your generated dashboard with stats. Go on, take a look at what your brand new performance dashboard looks like! 

To quickly iterate on how you would want the dashboard to look like use the command `make watch`. Every time a change is being made in the `source` folder it will output the changes in the `output` folder. This won't use data pulled from any metrics so if you want to see it with data you'll have to add that data in the `conf_dev.yml` file. You should look for words that ends with `_stat`.  

## Update the data every 24 hours 
When've made sure your dashboard builds successfully, which you can do with the command `make generate`. The next step is to make configurations for Travis CI.

You'll need to add secure github token to `.travis.yml`. The way to do that is described in [detail here](http://benlimmer.com/2013/12/26/automatically-publish-javadoc-to-gh-pages-with-travis-ci/). But in short you'll need to do the following. First delete the secure statement that isn't yours. Then get a [github token](https://github.com/settings/tokens) and use it below.

    sudo gem install travis
    travis encrypt GH_TOKEN=your_token --add

Then in the settings for Travis CI go on and add the following environment variables: `SD_AUTH_TOKEN` with a token from the app and `GH_REPO_SLUG` which is the path to your repo (ie in our case it would be `serverdensity/performance-dashboard`)

After that you start using the free service [Nightli.es](https://nightli.es) to continually build your performance dashboard every 24 hours. 

## Configuration
Let's walk through the configuration options that you can make in `conf.yml`. There are two base levels for the yaml file. `general` and `infrastructure`. For the general settings you have the following. 

| Name        | Required | Explanation |
|-------------| -------- | ------------|
| company     | yes      | Your company name |
| company-logo| no       | A small image of your logo |
| header      | yes      | Text below your company name |
| sub-header  | yes      | Smaller text below the header |
| header-image | no      | An image below the header area |
| statuspage  | no       | If you have a statuspage at statuspage.io it'll pull your status from there |
| stack       | no       | A list of your stack which will be displayed at the bottom of the page |
| round       | no       | Rounding of all numbers, defaults to 2 decimals |
| timeframe   | no       | The timeframe you want to display the data from. It defaults to `24` meaning that it will pull data from the last 24 hours. 

For the `infrastructure` heading there are the following settings. 

| Name       | Required  | Explanation |
|----------- | --------- | ----------- |
| title      | yes       | The title of the section |
| title_layout | no      | either left or right, defaults to left |
| subtitle   | no        | A smaller subtitle below the title |
| image      | no        | An image that you can display in the section, requires that you set image_layout |
| image_layout | no      | either left or right |
| size       | no        | The size of the section in percent, defaults to 100 and you can choose from 10, 20, 25, 33, 34, 50, 60, 66, 67, 75, 80, 90, 100 |
| group      | maybe     | The group name in Server Density, either tag or group is required |
| tag        | maybe     | The tag name in Server Density, either tag or group name is required |
| bubble-description | no | A description that shows up as a bubble above the metric |

Inside the `infrastructure` heading there is a `metrics` heading. The `metrics` heading takes a yaml list where you can make the following settings.  

| Name       | Required | Explanation |
|----------  | -------- | ----------- |
| metrickey  | yes      | After having done `make available`, you'll see all the possible keys, this is where you put it. |
| calculation | yes     | A yaml list of ways to make calculations for the metric. Possible values are `average`, `sum`, `max`, `median`, `min` |
| cumulative | no       | If the data is distributed among several servers and you want each data point summed. Useful for metrics that can be counted, such as requests, megabyte, users. Not to be used for things like load or CPU usage. *Defaults to True*| 
| si_unit    | no       | use `mb` as a value if you want to display GB, TB, PB instead of K, M and B. Defaults to normal usage. 
| *your_calc*_title | - | if you used average as a calculation method, it should be `average_title` |
| *your_calc*_unit | -  | if you used average as a calculation method, it should be `average_unit` |
| *your_calc*_stat | -  | if you used average as a calculation method, it should be `average_stat`, this is useful for dummy if you quickly want to see how things look when using `make generate_dev` |
| style      | no       | uses the different modules defined in `index.html`. The default style is `circle-frame`, and other styles are `circle-filled`, `square-frame` or `square-filled`. 

### Template
If you want to make any changes to the dashboard itself you can make the changes in the `index.html` file located in the templates folder.

### Config file
Here is an example of a [configuration file](https://github.com/serverdensity/performance-dashboard/blob/master/conf_dev.yml) and this is the [configuration file](https://github.com/serverdensity/performance-dashboard/blob/master/conf.yml) we used to make our dashboard. 

### Use a subdomain

If you want to use your own domain to host your performance dashboard, you'll need to create a CNAME file and set up a CNAME record pointing to that page with your DNS provider. There already is a CNAME file in the source folder. Change this to your own domain. 

If you have e.g. the domain `mydomain.com`, your GitHub repo is `my-repo` and you want your performance dashboard to be reachable at `performance.mydomain.com`

- Change the `CNAME` file in the source folder to 

        performance.mydomain.com
    
- Go to your DNS provider and create a new CNAME record pointing to your

          Name          Type      Value 
          performance   CNAME     myusername.github.io.

See [Using a custom domain with GitHub Pages](https://help.github.com/articles/custom-domain-redirects-for-github-pages-sites/) for more info.

## Modules

Below you can see what kind of modules currently exists to visualize the data. 

### Gallery
![Filled square](/docs/filled-square.png "Filled Square")
![Filled Circle](/docs/filled-circle.png "Filled Circle")
![Frame Circle](/docs/frame-circle.png "Frame Circle")
![Frame Square](/docs/frame-square.png "Frame Square")

### Explanation of they work

The code for the different modules currently lives in `templates/index.html`. It loops through all the calculation options you've defined in the `conf.yml` file. Such as `sum` or `max`. And displays it accordingly. Feel free to contribute more modules! 

```
{# The style called frame #}
{% macro frame(metric) -%}
    <div class="column">
        <div class="{{metric.style|default('square-frame')}} center-horizontal-child">
            {% for calculation in metric.calculation %}
            {% if loop.index == 1 %}
                <div class="frame-metric-stat">
                    <span class="frame-number">{{ short_no(metric[calculation + '_stat']) }}</span>
                    <span class="frame-unit">{{ metric[calculation + '_unit'] }}</span>
                </div>
                <span class="frame-stat-title">{{ metric[calculation + '_title'] }}</span>
            {% else %}
                <span class="frame-secondary-metric">
                    {{ metric[calculation + '_title'] }}: {{ short_no(metric[calculation + '_stat']) }} {{ metric[calculation + '_unit'] }}
                </span>
            {% endif %}
            {% endfor %}
        </div>
    </div>
{%- endmacro %}
```

<a name="myfootnote1">1</a>: It assumes that every device in your group uses the same metrics, so it only checks the first device to speed things up. 
