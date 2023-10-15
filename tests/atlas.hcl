data "external_schema" "sqlalchemy" {
  program = [
    "atlas-provider-sqlalchemy",
    "--path", "./models",    
    "--dialect", "mysql+pymysql", // mariadb | postgres | sqlite | mssql
  ]
}

env "sqlalchemy" {
  src = data.external_schema.sqlalchemy.url
  dev = "docker://mysql/8/dev"
  migration {
    dir = "file://migrations"
  }
  format {
    migrate {
      diff = "{{ sql . \"  \" }}"
    }
  }
}