{ "nodes": [
	{
		"id": "rf-server",
		"name": "RouteFlow Server",
		"adjacencies": [
			{
				"nodeTo": "controller",
				"nodeFrom": "rf-server",
				"data": {
					"$color": "#145D80"
				}
			}
		],
		"data": {
			"$type": "rf-server",
			"timer": 1332273377,
			"$dim": 20,
			"$x": -50,
			"$y": -170,
			"latitude": -21.950884,
			"longitude": -43.775578
		}
	},
	{
		"id": "controller",
		"name": "Controller",
		"adjacencies": [],
		"Label": {
			"$color": "#"
		},
		"data": {
			"$type": "controller",
			"timer": 1332273377,
			"$dim": 25,
			"$x": 100,
			"$y": -170,
			"latitude": -22.002466,
			"longitude": -46.062749
		}
	},
	{
		"id": "8",
		"name": "switch8",
		"adjacencies": [
			{
				"nodeTo": "controller",
				"nodeFrom": "8",
				"data": {
					"$color": "#145D80"
				}
			}
		],
		"data": {
			"$type": "of-switch",
			"timer": 1332273377,
			"$dim": 20,
			"latitude": -24,
			"longitude": -41
		}
	}]}